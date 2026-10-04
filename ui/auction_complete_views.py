from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from domains.auctionflow.intake_models import (
    AuctionOpeningSession, AuctionParticipantProfile, AuctionProposalIntake,
)
from domains.identity.models import AuditEvent
from domains.operations.models import AuctionLot, AuctionParticipant, AuctionPeriod, AuctionProposal, CommissionMember
from services.documents import store_document
from ui.fields import JalaliDateField


def _ip(request):
    return request.META.get("REMOTE_ADDR")


class ParticipantCompleteForm(forms.Form):
    name = forms.CharField(label="نام شرکت‌کننده / متقاضی", max_length=255)
    identity_number = forms.CharField(label="کد ملی / شناسه ملی", max_length=30, required=False)
    contact = forms.CharField(label="اطلاعات تماس خلاصه", max_length=120, required=False)
    kind = forms.ChoiceField(label="نوع شخص", choices=AuctionParticipantProfile.Kind.choices)
    father_name = forms.CharField(label="نام پدر", max_length=120, required=False)
    birth_certificate_number = forms.CharField(label="شماره شناسنامه", max_length=40, required=False)
    birth_date = JalaliDateField(label="تاریخ تولد", required=False)
    postal_code = forms.CharField(label="کدپستی", max_length=20, required=False)
    address = forms.CharField(label="نشانی", required=False, widget=forms.Textarea(attrs={"rows": 2}))
    phone = forms.CharField(label="تلفن", max_length=30, required=False)
    mobile = forms.CharField(label="همراه", max_length=20, required=False)
    legal_name = forms.CharField(label="نام حقوقی", max_length=255, required=False)
    registration_number = forms.CharField(label="شماره ثبت", max_length=60, required=False)
    economic_code = forms.CharField(label="کد اقتصادی", max_length=40, required=False)
    representative_name = forms.CharField(label="نماینده شخص حقوقی", max_length=255, required=False)
    notes = forms.CharField(label="توضیحات", required=False, widget=forms.Textarea(attrs={"rows": 2}))

    def __init__(self, *args, participant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if participant and not self.is_bound:
            profile = getattr(participant, "identity_profile", None)
            self.initial.update({"name": participant.name, "identity_number": participant.identity_number, "contact": participant.contact})
            if profile:
                for field in (
                    "kind", "father_name", "birth_certificate_number", "birth_date", "postal_code", "address",
                    "phone", "mobile", "legal_name", "registration_number", "economic_code", "representative_name", "notes",
                ):
                    self.initial[field] = getattr(profile, field)


class ProposalCompleteForm(forms.ModelForm):
    attachment = forms.FileField(label="فایل سند / پاکات", required=False)
    receipt_number = forms.CharField(label="شماره رسید دبیرخانه", max_length=80, required=False)
    intake_notes = forms.CharField(label="توضیحات دریافت", required=False, widget=forms.Textarea(attrs={"rows": 2}))
    envelope_b_decision = forms.ChoiceField(label="نتیجه اعلام‌شده بررسی پاکت ب", choices=AuctionProposalIntake.EnvelopeBDecision.choices)
    c_opening_allowed = forms.TypedChoiceField(
        label="اجازه بازگشایی پاکت ج توسط جلسه", required=False, coerce=lambda value: {"1": True, "0": False}.get(value),
        choices=(("", "هنوز تعیین نشده"), ("1", "مجاز است"), ("0", "مجاز نیست")), empty_value=None,
    )
    decision_note = forms.CharField(label="شرح تصمیم جلسه", required=False, widget=forms.Textarea(attrs={"rows": 2}))

    class Meta:
        model = AuctionProposal
        fields = [
            "participant", "received_at", "envelope_a_received", "envelope_b_received",
            "envelope_c_received", "offered_amount_rial", "status",
        ]
        labels = {
            "participant": "شرکت‌کننده", "received_at": "زمان دریافت",
            "envelope_a_received": "پاکت الف دریافت شد", "envelope_b_received": "پاکت ب دریافت شد",
            "envelope_c_received": "پاکت ج دریافت شد", "offered_amount_rial": "مبلغ پیشنهادی (ریال)",
            "status": "وضعیت پیشنهاد / پاکات",
        }
        widgets = {
            "received_at": forms.DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"),
            "offered_amount_rial": forms.NumberInput(attrs={"min": "0", "step": "1", "inputmode": "numeric"}),
        }

    def __init__(self, *args, lot=None, proposal=None, **kwargs):
        self.lot = lot
        super().__init__(*args, **kwargs)
        self.fields["received_at"].input_formats = ["%Y-%m-%dT%H:%M"]
        self.fields["participant"].queryset = AuctionParticipant.objects.filter(period=lot.period).order_by("name", "pk") if lot else AuctionParticipant.objects.none()
        if proposal and not self.is_bound:
            intake = getattr(proposal, "intake", None)
            if intake:
                self.initial.update({
                    "receipt_number": intake.receipt_number, "intake_notes": intake.notes,
                    "envelope_b_decision": intake.envelope_b_decision,
                    "c_opening_allowed": "1" if intake.c_opening_allowed is True else ("0" if intake.c_opening_allowed is False else ""),
                    "decision_note": intake.decision_note,
                })

    def clean(self):
        cleaned = super().clean()
        participant = cleaned.get("participant")
        if self.lot and participant:
            qs = AuctionProposal.objects.filter(lot=self.lot, participant=participant)
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                self.add_error("participant", "برای این شرکت‌کننده و این ردیف مزایده قبلاً پیشنهاد ثبت شده است.")
        if cleaned.get("envelope_c_received") and cleaned.get("c_opening_allowed") is not True:
            self.add_error("envelope_c_received", "ثبت دریافت/بازگشایی پاکت ج فقط پس از ثبت اجازه جلسه مجاز است.")
        if cleaned.get("envelope_b_decision") == AuctionProposalIntake.EnvelopeBDecision.REJECTED and cleaned.get("c_opening_allowed") is True:
            self.add_error("c_opening_allowed", "برای پاکت ب ردشده، اجازه بازگشایی پاکت ج قابل ثبت نیست.")
        return cleaned


class OpeningSessionForm(forms.Form):
    session_date = JalaliDateField(label="تاریخ جلسه")
    session_time = forms.CharField(label="ساعت", max_length=5, required=False)
    location = forms.CharField(label="محل جلسه", max_length=255, required=False)
    reference = forms.CharField(label="شماره / مرجع جلسه", max_length=255, required=False)
    state = forms.ChoiceField(label="وضعیت جلسه", choices=AuctionOpeningSession.State.choices)
    declared_summary = forms.CharField(label="خلاصه نتیجه اعلام‌شده", required=False, widget=forms.Textarea(attrs={"rows": 3}))
    signature_note = forms.CharField(label="توضیحات امضا / صورتجلسه", required=False, widget=forms.Textarea(attrs={"rows": 2}))


@login_required
@transaction.atomic
def participant_create(request, period_id):
    period = get_object_or_404(AuctionPeriod, pk=period_id)
    form = ParticipantCompleteForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        participant = AuctionParticipant.objects.create(
            period=period, name=form.cleaned_data["name"].strip(),
            identity_number=form.cleaned_data["identity_number"].strip(), contact=form.cleaned_data["contact"].strip(),
        )
        values = {key: form.cleaned_data.get(key, "") for key in (
            "kind", "father_name", "birth_certificate_number", "birth_date", "postal_code", "address", "phone", "mobile",
            "legal_name", "registration_number", "economic_code", "representative_name", "notes",
        )}
        AuctionParticipantProfile.objects.create(participant=participant, updated_by=request.user, **values)
        AuditEvent.objects.create(actor=request.user, action="AUCTION_PARTICIPANT_CREATE", entity_type="AuctionPeriod", entity_id=str(period.pk), after={"participant_id": participant.pk, "name": participant.name, "identity_number": participant.identity_number, "kind": values["kind"]}, ip_address=_ip(request))
        messages.success(request, "مشخصات کامل شرکت‌کننده مزایده ثبت شد.")
        return redirect("auction-period-detail", period_id=period.pk)
    return render(request, "ui/entity_form.html", {"form": form, "title": f"ثبت شرکت‌کننده — {period.title}", "subtitle": "این مشخصات در صورت اعلام برنده، منبع تکمیل خودکار بهره‌بردار و نمونه قرارداد خواهد بود.", "cancel_url": "auction-period-detail", "cancel_kwargs": {"period_id": period.pk}})


@login_required
@transaction.atomic
def participant_edit(request, participant_id):
    participant = get_object_or_404(AuctionParticipant, pk=participant_id)
    profile, _ = AuctionParticipantProfile.objects.get_or_create(participant=participant, defaults={"updated_by": request.user})
    form = ParticipantCompleteForm(request.POST or None, participant=participant)
    if request.method == "POST" and form.is_valid():
        before = {"name": participant.name, "identity_number": participant.identity_number, "contact": participant.contact}
        participant.name = form.cleaned_data["name"].strip(); participant.identity_number = form.cleaned_data["identity_number"].strip(); participant.contact = form.cleaned_data["contact"].strip(); participant.save()
        for field in ("kind", "father_name", "birth_certificate_number", "birth_date", "postal_code", "address", "phone", "mobile", "legal_name", "registration_number", "economic_code", "representative_name", "notes"):
            setattr(profile, field, form.cleaned_data.get(field, ""))
        profile.updated_by = request.user; profile.save()
        AuditEvent.objects.create(actor=request.user, action="AUCTION_PARTICIPANT_UPDATE", entity_type="AuctionPeriod", entity_id=str(participant.period_id), before=before, after={"participant_id": participant.pk, "name": participant.name, "identity_number": participant.identity_number, "kind": profile.kind}, reason=request.POST.get("change_reason", "").strip(), ip_address=_ip(request))
        messages.success(request, "مشخصات شرکت‌کننده به‌روزرسانی شد.")
        return redirect("auction-period-detail", period_id=participant.period_id)
    return render(request, "ui/entity_form.html", {"form": form, "title": f"ویرایش شرکت‌کننده — {participant.name}", "subtitle": "ویرایش سابقه‌دار است؛ اطلاعات قرارداد آینده از همین پرونده خوانده می‌شود.", "show_change_reason": True, "cancel_url": "auction-period-detail", "cancel_kwargs": {"period_id": participant.period_id}})


def _save_intake(*, proposal, cleaned, actor):
    intake, _ = AuctionProposalIntake.objects.get_or_create(proposal=proposal, defaults={"registrar": actor})
    intake.receipt_number = cleaned.get("receipt_number", "").strip()
    intake.notes = cleaned.get("intake_notes", "").strip()
    intake.envelope_b_decision = cleaned.get("envelope_b_decision") or AuctionProposalIntake.EnvelopeBDecision.PENDING
    intake.c_opening_allowed = cleaned.get("c_opening_allowed")
    intake.decision_note = cleaned.get("decision_note", "").strip()
    intake.registrar = actor
    intake.save()
    return intake


@login_required
@transaction.atomic
def proposal_create(request, lot_id):
    lot = get_object_or_404(AuctionLot.objects.select_related("period", "space"), pk=lot_id)
    form = ProposalCompleteForm(request.POST or None, request.FILES or None, lot=lot)
    if request.method == "POST" and form.is_valid():
        proposal = form.save(commit=False); proposal.lot = lot; proposal.save()
        intake = _save_intake(proposal=proposal, cleaned=form.cleaned_data, actor=request.user)
        uploaded = form.cleaned_data.get("attachment")
        if uploaded:
            proposal.document = store_document(uploaded=uploaded, title=f"اسناد پاکات مزایده — فضای {lot.space.code}", document_type="AUCTION_ENVELOPES", entity_type="AuctionProposal", entity_id=proposal.pk, user=request.user, reference=lot.period.identity, notes=f"پیشنهاد شرکت‌کننده: {proposal.participant.name}; رسید: {intake.receipt_number}", ip_address=_ip(request)); proposal.save(update_fields=["document"])
        AuditEvent.objects.create(actor=request.user, action="AUCTION_PROPOSAL_CREATE", entity_type="AuctionPeriod", entity_id=str(lot.period_id), after={"proposal_id": proposal.pk, "lot_id": lot.pk, "participant_id": proposal.participant_id, "receipt_number": intake.receipt_number, "envelope_a": proposal.envelope_a_received, "envelope_b": proposal.envelope_b_received, "envelope_b_decision": intake.envelope_b_decision, "c_opening_allowed": intake.c_opening_allowed, "envelope_c": proposal.envelope_c_received, "offered_amount_rial": str(proposal.offered_amount_rial) if proposal.offered_amount_rial is not None else None}, ip_address=_ip(request))
        messages.success(request, "دریافت پیشنهاد، رسید و وضعیت پاکات ثبت شد.")
        return redirect("auction-period-detail", period_id=lot.period_id)
    return render(request, "ui/auction_proposal_form.html", {"form": form, "lot": lot, "title": f"ثبت دریافت پیشنهاد — فضای {lot.space.code}"})


@login_required
@transaction.atomic
def proposal_edit(request, proposal_id):
    proposal = get_object_or_404(AuctionProposal.objects.select_related("lot__period", "lot__space", "participant", "document"), pk=proposal_id)
    form = ProposalCompleteForm(request.POST or None, request.FILES or None, instance=proposal, lot=proposal.lot, proposal=proposal)
    if request.method == "POST" and form.is_valid():
        before = {"participant_id": proposal.participant_id, "envelope_a": proposal.envelope_a_received, "envelope_b": proposal.envelope_b_received, "envelope_c": proposal.envelope_c_received, "offered_amount_rial": str(proposal.offered_amount_rial) if proposal.offered_amount_rial is not None else None}
        updated = form.save(); intake = _save_intake(proposal=updated, cleaned=form.cleaned_data, actor=request.user)
        uploaded = form.cleaned_data.get("attachment")
        if uploaded:
            updated.document = store_document(uploaded=uploaded, title=f"اسناد پاکات مزایده — فضای {updated.lot.space.code}", document_type="AUCTION_ENVELOPES", entity_type="AuctionProposal", entity_id=updated.pk, user=request.user, reference=updated.lot.period.identity, notes=f"نسخه جدید سند پیشنهاد: {updated.participant.name}; رسید: {intake.receipt_number}", ip_address=_ip(request)); updated.save(update_fields=["document"])
        AuditEvent.objects.create(actor=request.user, action="AUCTION_PROPOSAL_UPDATE", entity_type="AuctionPeriod", entity_id=str(updated.lot.period_id), before=before, after={"proposal_id": updated.pk, "receipt_number": intake.receipt_number, "envelope_b_decision": intake.envelope_b_decision, "c_opening_allowed": intake.c_opening_allowed, "envelope_c": updated.envelope_c_received, "offered_amount_rial": str(updated.offered_amount_rial) if updated.offered_amount_rial is not None else None}, reason=request.POST.get("change_reason", "").strip(), ip_address=_ip(request))
        messages.success(request, "اطلاعات دریافت و پاکات به‌روزرسانی شد.")
        return redirect("auction-period-detail", period_id=updated.lot.period_id)
    return render(request, "ui/auction_proposal_form.html", {"form": form, "lot": proposal.lot, "proposal": proposal, "title": f"ویرایش دریافت پیشنهاد — فضای {proposal.lot.space.code}", "show_change_reason": True})


@login_required
@transaction.atomic
def opening_session_create(request, period_id):
    period = get_object_or_404(AuctionPeriod, pk=period_id)
    form = OpeningSessionForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        members = list(CommissionMember.objects.filter(status=CommissionMember.Status.ACTIVE).order_by("sign_order", "pk").values("name", "position", "role", "sign_order"))
        session = AuctionOpeningSession.objects.create(period=period, member_snapshot=members, created_by=request.user, **form.cleaned_data)
        AuditEvent.objects.create(actor=request.user, action="AUCTION_OPENING_SESSION_CREATE", entity_type="AuctionPeriod", entity_id=str(period.pk), after={"session_id": session.pk, "date": session.session_date, "state": session.state, "member_count": len(members)}, ip_address=_ip(request))
        messages.success(request, "جلسه بازگشایی با Snapshot اعضای فعال کمیسیون ثبت شد.")
        return redirect("auction-period-detail", period_id=period.pk)
    return render(request, "ui/entity_form.html", {"form": form, "title": f"ثبت جلسه بازگشایی — {period.title}", "subtitle": "اعضای فعال کمیسیون در لحظه ثبت Snapshot می‌شوند و نتیجه فقط به‌عنوان نتیجه اعلام‌شده جلسه ذخیره می‌شود.", "cancel_url": "auction-period-detail", "cancel_kwargs": {"period_id": period.pk}})


@login_required
@transaction.atomic
def winner_select(request, lot_id):
    from services.auction_flow import select_winner
    from services.dates import normalize_jalali
    lot = get_object_or_404(AuctionLot.objects.select_related("period", "space"), pk=lot_id)
    if request.method != "POST":
        return redirect("auction-period-detail", period_id=lot.period_id)
    try:
        winner = get_object_or_404(AuctionProposal.objects.select_related("participant"), pk=int(request.POST.get("winner_proposal_id", "0")))
        intake = getattr(winner, "intake", None)
        if not intake or intake.envelope_b_decision != AuctionProposalIntake.EnvelopeBDecision.ACCEPTED or intake.c_opening_allowed is not True:
            raise ValidationError("تعیین برنده فقط پس از ثبت تأیید پاکت ب و اجازه بازگشایی پاکت ج توسط جلسه مجاز است.")
        runner = None
        runner_id = (request.POST.get("runner_up_proposal_id") or "").strip()
        if runner_id.isdigit():
            runner = get_object_or_404(AuctionProposal.objects.select_related("participant"), pk=int(runner_id))
        decision_date = normalize_jalali(request.POST.get("decision_date", ""))
        profile = select_winner(lot=lot, winner_proposal=winner, runner_up_proposal=runner, decision_reference=request.POST.get("decision_reference", ""), decision_date=decision_date, actor=request.user, ip_address=_ip(request))
    except (ValidationError, ValueError) as exc:
        messages.error(request, " ".join(getattr(exc, "messages", [str(exc)])))
    else:
        messages.success(request, f"نتیجه اعلام‌شده جلسه ثبت شد؛ برنده: {profile.winner_proposal.participant.name}. سما برنده را محاسبه نکرده است.")
    return redirect("auction-period-detail", period_id=lot.period_id)
