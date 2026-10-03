from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from domains.documents.models import Document
from domains.identity.models import AuditEvent
from domains.operations.models import AuctionLot, AuctionParticipant, AuctionPeriod, AuctionProposal
from services.documents import store_document
from ui.fields import JalaliDateField


def _ip(request):
    return request.META.get("REMOTE_ADDR")


class AuctionParticipantForm(forms.ModelForm):
    class Meta:
        model = AuctionParticipant
        fields = ["name", "identity_number", "contact"]
        labels = {
            "name": "نام شرکت‌کننده / متقاضی",
            "identity_number": "کد ملی / شناسه ملی",
            "contact": "اطلاعات تماس",
        }


class AuctionProposalForm(forms.ModelForm):
    attachment = forms.FileField(label="فایل سند / پاکات", required=False)

    class Meta:
        model = AuctionProposal
        fields = [
            "participant", "received_at", "envelope_a_received", "envelope_b_received",
            "envelope_c_received", "offered_amount_rial", "status",
        ]
        labels = {
            "participant": "شرکت‌کننده",
            "received_at": "زمان دریافت",
            "envelope_a_received": "پاکت A دریافت شد",
            "envelope_b_received": "پاکت B دریافت شد",
            "envelope_c_received": "پاکت C دریافت شد",
            "offered_amount_rial": "مبلغ پیشنهادی (ریال)",
            "status": "وضعیت پیشنهاد / پاکات",
        }
        widgets = {
            "received_at": forms.DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"),
            "offered_amount_rial": forms.NumberInput(attrs={"min": "0", "step": "1", "inputmode": "numeric"}),
        }

    def __init__(self, *args, lot=None, **kwargs):
        self.lot = lot
        super().__init__(*args, **kwargs)
        self.fields["received_at"].input_formats = ["%Y-%m-%dT%H:%M"]
        if lot:
            self.fields["participant"].queryset = AuctionParticipant.objects.filter(period=lot.period).order_by("name", "pk")
        else:
            self.fields["participant"].queryset = AuctionParticipant.objects.none()

    def clean(self):
        cleaned = super().clean()
        participant = cleaned.get("participant")
        if self.lot and participant:
            qs = AuctionProposal.objects.filter(lot=self.lot, participant=participant)
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                self.add_error("participant", "برای این شرکت‌کننده و این ردیف مزایده قبلاً پیشنهاد ثبت شده است.")
        amount = cleaned.get("offered_amount_rial")
        if amount is not None and amount < 0:
            self.add_error("offered_amount_rial", "مبلغ پیشنهادی نمی‌تواند منفی باشد.")
        return cleaned


class AuctionPeriodDocumentForm(forms.Form):
    title = forms.CharField(label="عنوان سند", max_length=255)
    document_type = forms.CharField(label="نوع سند مزایده", max_length=80)
    reference = forms.CharField(label="شماره / مرجع", max_length=255, required=False)
    document_date = JalaliDateField(label="تاریخ سند", required=False)
    notes = forms.CharField(label="توضیحات", required=False, widget=forms.Textarea(attrs={"rows": 2}))
    file = forms.FileField(label="فایل")


@login_required
def auction_period_detail(request, period_id):
    period = get_object_or_404(
        AuctionPeriod.objects.prefetch_related(
            "lots__space", "lots__proposals__participant", "participants"
        ),
        pk=period_id,
    )
    documents = Document.objects.filter(
        entity_type="AuctionPeriod", entity_id=str(period.pk), archived_at__isnull=True
    ).order_by("-uploaded_at", "-pk")
    return render(request, "ui/auction_period_detail.html", {
        "period": period,
        "documents": documents,
    })


@login_required
@transaction.atomic
def auction_participant_create(request, period_id):
    period = get_object_or_404(AuctionPeriod, pk=period_id)
    form = AuctionParticipantForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        participant = form.save(commit=False)
        participant.period = period
        participant.save()
        AuditEvent.objects.create(
            actor=request.user, action="AUCTION_PARTICIPANT_CREATE",
            entity_type="AuctionPeriod", entity_id=str(period.pk),
            after={"participant_id": participant.pk, "name": participant.name, "identity_number": participant.identity_number},
            ip_address=_ip(request),
        )
        messages.success(request, "شرکت‌کننده مزایده ثبت شد.")
        return redirect("auction-period-detail", period_id=period.pk)
    return render(request, "ui/entity_form.html", {
        "form": form,
        "title": f"ثبت شرکت‌کننده — {period.title}",
        "subtitle": "اطلاعات شرکت‌کننده یک‌بار ثبت و سپس از صفحه دوره قابل ویرایش است.",
        "cancel_url": "auction-period-detail",
        "cancel_kwargs": {"period_id": period.pk},
    })


@login_required
@transaction.atomic
def auction_participant_edit(request, participant_id):
    participant = get_object_or_404(AuctionParticipant, pk=participant_id)
    before = {"name": participant.name, "identity_number": participant.identity_number, "contact": participant.contact}
    form = AuctionParticipantForm(request.POST or None, instance=participant)
    if request.method == "POST" and form.is_valid():
        updated = form.save()
        AuditEvent.objects.create(
            actor=request.user, action="AUCTION_PARTICIPANT_UPDATE",
            entity_type="AuctionPeriod", entity_id=str(updated.period_id),
            before=before,
            after={"participant_id": updated.pk, "name": updated.name, "identity_number": updated.identity_number, "contact": updated.contact},
            reason=request.POST.get("change_reason", "").strip(), ip_address=_ip(request),
        )
        messages.success(request, "اطلاعات شرکت‌کننده به‌روزرسانی شد.")
        return redirect("auction-period-detail", period_id=updated.period_id)
    return render(request, "ui/entity_form.html", {
        "form": form,
        "title": f"ویرایش شرکت‌کننده — {participant.name}",
        "subtitle": "ویرایش سابقه‌دار است و ثبت مجدد شرکت‌کننده لازم نیست.",
        "show_change_reason": True,
        "cancel_url": "auction-period-detail",
        "cancel_kwargs": {"period_id": participant.period_id},
    })


@login_required
@transaction.atomic
def auction_proposal_create(request, lot_id):
    lot = get_object_or_404(AuctionLot.objects.select_related("period", "space"), pk=lot_id)
    form = AuctionProposalForm(request.POST or None, request.FILES or None, lot=lot)
    if request.method == "POST" and form.is_valid():
        proposal = form.save(commit=False)
        proposal.lot = lot
        proposal.save()
        uploaded = form.cleaned_data.get("attachment")
        if uploaded:
            document = store_document(
                uploaded=uploaded,
                title=f"اسناد پاکات مزایده — فضای {lot.space.code}",
                document_type="AUCTION_ENVELOPES",
                entity_type="AuctionProposal",
                entity_id=proposal.pk,
                user=request.user,
                reference=lot.period.identity,
                notes=f"پیشنهاد شرکت‌کننده: {proposal.participant.name}",
                ip_address=_ip(request),
            )
            proposal.document = document
            proposal.save(update_fields=["document"])
        AuditEvent.objects.create(
            actor=request.user, action="AUCTION_PROPOSAL_CREATE",
            entity_type="AuctionPeriod", entity_id=str(lot.period_id),
            after={
                "proposal_id": proposal.pk, "lot_id": lot.pk, "participant_id": proposal.participant_id,
                "envelope_a": proposal.envelope_a_received, "envelope_b": proposal.envelope_b_received,
                "envelope_c": proposal.envelope_c_received,
                "offered_amount_rial": str(proposal.offered_amount_rial) if proposal.offered_amount_rial is not None else None,
                "status": proposal.status, "document_id": proposal.document_id,
            },
            ip_address=_ip(request),
        )
        messages.success(request, "دریافت پاکات / پیشنهاد ثبت شد.")
        return redirect("auction-period-detail", period_id=lot.period_id)
    return render(request, "ui/auction_proposal_form.html", {
        "form": form, "lot": lot, "title": f"ثبت پاکات و پیشنهاد — فضای {lot.space.code}",
    })


@login_required
@transaction.atomic
def auction_proposal_edit(request, proposal_id):
    proposal = get_object_or_404(
        AuctionProposal.objects.select_related("lot__period", "lot__space", "participant", "document"), pk=proposal_id
    )
    before = {
        "participant_id": proposal.participant_id, "envelope_a": proposal.envelope_a_received,
        "envelope_b": proposal.envelope_b_received, "envelope_c": proposal.envelope_c_received,
        "offered_amount_rial": str(proposal.offered_amount_rial) if proposal.offered_amount_rial is not None else None,
        "status": proposal.status, "document_id": proposal.document_id,
    }
    form = AuctionProposalForm(request.POST or None, request.FILES or None, instance=proposal, lot=proposal.lot)
    if request.method == "POST" and form.is_valid():
        updated = form.save()
        uploaded = form.cleaned_data.get("attachment")
        if uploaded:
            document = store_document(
                uploaded=uploaded,
                title=f"اسناد پاکات مزایده — فضای {updated.lot.space.code}",
                document_type="AUCTION_ENVELOPES",
                entity_type="AuctionProposal", entity_id=updated.pk, user=request.user,
                reference=updated.lot.period.identity,
                notes=f"نسخه جدید سند پیشنهاد: {updated.participant.name}", ip_address=_ip(request),
            )
            updated.document = document
            updated.save(update_fields=["document"])
        AuditEvent.objects.create(
            actor=request.user, action="AUCTION_PROPOSAL_UPDATE",
            entity_type="AuctionPeriod", entity_id=str(updated.lot.period_id), before=before,
            after={
                "proposal_id": updated.pk, "participant_id": updated.participant_id,
                "envelope_a": updated.envelope_a_received, "envelope_b": updated.envelope_b_received,
                "envelope_c": updated.envelope_c_received,
                "offered_amount_rial": str(updated.offered_amount_rial) if updated.offered_amount_rial is not None else None,
                "status": updated.status, "document_id": updated.document_id,
            },
            reason=request.POST.get("change_reason", "").strip(), ip_address=_ip(request),
        )
        messages.success(request, "اطلاعات پاکات / پیشنهاد به‌روزرسانی شد.")
        return redirect("auction-period-detail", period_id=updated.lot.period_id)
    return render(request, "ui/auction_proposal_form.html", {
        "form": form, "lot": proposal.lot, "proposal": proposal,
        "title": f"ویرایش پاکات و پیشنهاد — فضای {proposal.lot.space.code}",
        "show_change_reason": True,
    })


@login_required
@transaction.atomic
def auction_period_document_upload(request, period_id):
    period = get_object_or_404(AuctionPeriod, pk=period_id)
    form = AuctionPeriodDocumentForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        store_document(
            uploaded=form.cleaned_data["file"], title=form.cleaned_data["title"],
            document_type=form.cleaned_data["document_type"], entity_type="AuctionPeriod", entity_id=period.pk,
            user=request.user, reference=form.cleaned_data.get("reference", ""),
            document_date=form.cleaned_data.get("document_date", ""), notes=form.cleaned_data.get("notes", ""),
            ip_address=_ip(request),
        )
        messages.success(request, "سند مزایده ثبت شد.")
        return redirect("auction-period-detail", period_id=period.pk)
    return render(request, "ui/auction_document_form.html", {"form": form, "period": period})
