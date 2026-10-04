import jdatetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect

from domains.auctionflow.intake_models import AuctionContractDraft
from domains.auctionflow.models import AuctionDocumentInstance, AuctionLotProfile, AuctionPeriodProfile
from domains.contracts.models import Beneficiary
from domains.identity.models import AuditEvent
from domains.operations.models import AuctionLot
from services.auction_complete_documents import generate_complete_document
from services.auction_flow import start_contract_from_award
from services.dates import normalize_jalali


def _ip(request):
    return request.META.get("REMOTE_ADDR")


def _add_years_jalali(value, years):
    year, month, day = (int(part) for part in value.split("/"))
    target_year = year + years
    if month == 12 and day == 30 and not jdatetime.date(target_year, 1, 1).isleap():
        day = 29
    return jdatetime.date(target_year, month, day).strftime("%Y/%m/%d")


@login_required
@transaction.atomic
def contract_start(request, lot_id):
    lot = get_object_or_404(AuctionLot.objects.select_related("period", "space"), pk=lot_id)
    if request.method != "POST":
        return redirect("auction-period-detail", period_id=lot.period_id)
    profile, _ = AuctionLotProfile.objects.get_or_create(lot=lot)
    if not profile.winner_proposal_id:
        messages.error(request, "ابتدا نتیجه اعلام‌شده و برنده مزایده را ثبت کنید.")
        return redirect("auction-period-detail", period_id=lot.period_id)
    try:
        start_date = normalize_jalali(request.POST.get("operational_start_date", ""))
        if not start_date:
            raise ValidationError("تاریخ شروع قرارداد الزامی است.")
        period_profile, _ = AuctionPeriodProfile.objects.get_or_create(period=lot.period)
        end_date = _add_years_jalali(start_date, int(period_profile.duration_years or 1))
        winner = profile.winner_proposal.participant
        identity = getattr(winner, "identity_profile", None)
        kind = Beneficiary.Kind.LEGAL if identity and identity.kind == "LEGAL" else Beneficiary.Kind.NATURAL
        circulation = start_contract_from_award(
            lot=lot, actor=request.user, beneficiary_kind=kind,
            operational_start_date=start_date,
            due_date=normalize_jalali(request.POST.get("due_date", "")) if request.POST.get("due_date") else "",
            ip_address=_ip(request),
        )
        beneficiary = circulation.beneficiary
        if identity:
            beneficiary.kind = kind
            beneficiary.father_name = identity.father_name
            beneficiary.birth_certificate_number = identity.birth_certificate_number
            beneficiary.birth_date = identity.birth_date
            beneficiary.postal_code = identity.postal_code
            beneficiary.address = identity.address
            beneficiary.phone = identity.phone
            beneficiary.mobile = identity.mobile
            beneficiary.legal_name = identity.legal_name
            beneficiary.registration_number = identity.registration_number
            beneficiary.economic_code = identity.economic_code
            beneficiary.representative_name = identity.representative_name
            beneficiary.save()
        amount = profile.winner_proposal.offered_amount_rial
        if amount is None:
            raise ValidationError("مبلغ پیشنهاد برنده ثبت نشده است.")
        draft, _ = AuctionContractDraft.objects.update_or_create(
            lot=lot,
            defaults={
                "subject": f"واگذاری و بهره‌برداری فضای {lot.space.code} بر اساس نتیجه مزایده {lot.period.identity}",
                "start_date": start_date,
                "end_date": end_date,
                "amount_rial": amount,
                "investment_commitment_rial": profile.investment_amount_rial,
                "created_by": request.user,
            },
        )
        AuditEvent.objects.create(
            actor=request.user, action="AUCTION_CONTRACT_DRAFT_CREATED", entity_type="AuctionLot", entity_id=str(lot.pk),
            after={"circulation_id": circulation.pk, "start_date": draft.start_date, "end_date": draft.end_date,
                   "amount_rial": str(draft.amount_rial), "beneficiary_id": beneficiary.pk}, ip_address=_ip(request),
        )
    except (ValidationError, ValueError) as exc:
        messages.error(request, " ".join(getattr(exc, "messages", [str(exc)])))
        return redirect("auction-period-detail", period_id=lot.period_id)
    messages.success(request, f"گردش قرارداد {circulation.identity} ایجاد و اطلاعات برنده برای قرارداد تکمیل شد. نمونه قرارداد اکنون قابل تولید است.")
    return redirect("contract-circulation-detail", pk=circulation.pk)


@login_required
@transaction.atomic
def document_generate(request, lot_id, document_type):
    lot = get_object_or_404(AuctionLot.objects.select_related("period", "space"), pk=lot_id)
    if request.method != "POST":
        return redirect("auction-period-detail", period_id=lot.period_id)
    if document_type not in AuctionDocumentInstance.DocumentType.values:
        messages.error(request, "نوع سند درخواستی معتبر نیست.")
        return redirect("auction-period-detail", period_id=lot.period_id)
    try:
        instance = generate_complete_document(lot=lot, document_type=document_type, actor=request.user, ip_address=_ip(request))
    except ValidationError as exc:
        messages.error(request, " ".join(exc.messages))
    else:
        messages.success(request, f"{instance.get_document_type_display()} از Master Source قفل‌شده و داده‌های جاری سما تولید شد.")
    return redirect("auction-period-detail", period_id=lot.period_id)
