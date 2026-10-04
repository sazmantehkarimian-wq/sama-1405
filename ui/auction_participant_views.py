from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from domains.auctionflow.intake_models import AuctionParticipantProfile
from domains.identity.models import AuditEvent
from domains.operations.models import AuctionParticipant, AuctionPeriod
from ui.auction_complete_views import ParticipantCompleteForm


def _ip(request):
    return request.META.get("REMOTE_ADDR")


def _normalized_post(request):
    if request.method != "POST":
        return None
    data = request.POST.copy()
    if not data.get("kind"):
        data["kind"] = AuctionParticipantProfile.Kind.NATURAL
    return data


@login_required
@transaction.atomic
def participant_create(request, period_id):
    period = get_object_or_404(AuctionPeriod, pk=period_id)
    form = ParticipantCompleteForm(_normalized_post(request))
    if request.method == "POST" and form.is_valid():
        participant = AuctionParticipant.objects.create(
            period=period,
            name=form.cleaned_data["name"].strip(),
            identity_number=form.cleaned_data["identity_number"].strip(),
            contact=form.cleaned_data["contact"].strip(),
        )
        values = {key: form.cleaned_data.get(key, "") for key in (
            "kind", "father_name", "birth_certificate_number", "birth_date", "postal_code", "address",
            "phone", "mobile", "legal_name", "registration_number", "economic_code", "representative_name", "notes",
        )}
        values["kind"] = values.get("kind") or AuctionParticipantProfile.Kind.NATURAL
        AuctionParticipantProfile.objects.create(participant=participant, updated_by=request.user, **values)
        AuditEvent.objects.create(
            actor=request.user, action="AUCTION_PARTICIPANT_CREATE", entity_type="AuctionPeriod", entity_id=str(period.pk),
            after={"participant_id": participant.pk, "name": participant.name, "identity_number": participant.identity_number, "kind": values["kind"]},
            ip_address=_ip(request),
        )
        messages.success(request, "مشخصات کامل متقاضی مزایده ثبت شد.")
        return redirect("auction-period-detail", period_id=period.pk)
    return render(request, "ui/auction_participant_form.html", {
        "form": form, "period": period, "title": f"ثبت متقاضی — {period.title}",
        "subtitle": "مشخصات ثبت‌شده در صورت اعلام برنده، منبع تکمیل خودکار بهره‌بردار و نمونه قرارداد خواهد بود.",
    })


@login_required
@transaction.atomic
def participant_edit(request, participant_id):
    participant = get_object_or_404(AuctionParticipant, pk=participant_id)
    profile, _ = AuctionParticipantProfile.objects.get_or_create(
        participant=participant, defaults={"updated_by": request.user, "kind": AuctionParticipantProfile.Kind.NATURAL},
    )
    form = ParticipantCompleteForm(_normalized_post(request), participant=participant)
    if request.method == "POST" and form.is_valid():
        before = {"name": participant.name, "identity_number": participant.identity_number, "contact": participant.contact, "kind": profile.kind}
        participant.name = form.cleaned_data["name"].strip()
        participant.identity_number = form.cleaned_data["identity_number"].strip()
        participant.contact = form.cleaned_data["contact"].strip()
        participant.save()
        for field in (
            "kind", "father_name", "birth_certificate_number", "birth_date", "postal_code", "address", "phone", "mobile",
            "legal_name", "registration_number", "economic_code", "representative_name", "notes",
        ):
            value = form.cleaned_data.get(field, "")
            if field == "kind" and not value:
                value = AuctionParticipantProfile.Kind.NATURAL
            setattr(profile, field, value)
        profile.updated_by = request.user
        profile.save()
        AuditEvent.objects.create(
            actor=request.user, action="AUCTION_PARTICIPANT_UPDATE", entity_type="AuctionPeriod", entity_id=str(participant.period_id),
            before=before,
            after={"participant_id": participant.pk, "name": participant.name, "identity_number": participant.identity_number, "kind": profile.kind},
            reason=request.POST.get("change_reason", "").strip(), ip_address=_ip(request),
        )
        messages.success(request, "مشخصات متقاضی به‌روزرسانی شد.")
        return redirect("auction-period-detail", period_id=participant.period_id)
    return render(request, "ui/auction_participant_form.html", {
        "form": form, "period": participant.period, "participant": participant,
        "title": f"ویرایش متقاضی — {participant.name}",
        "subtitle": "ویرایش سابقه‌دار است؛ اطلاعات قرارداد آینده از همین پرونده خوانده می‌شود.",
        "show_change_reason": True,
    })
