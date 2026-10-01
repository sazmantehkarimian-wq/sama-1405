from decimal import Decimal, InvalidOperation
from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q

from domains.contracts.models import BeneficiaryAssignment, Contract, ContractAmendment
from domains.identity.models import AuditEvent
from domains.operations.models import OperationalHistory, TimelineEvent
from services.database import retry_locked
from services.dates import normalize_jalali
from services.text import normalize_persian_text


def effective_contract(queryset, on_date):
    return (
        queryset.filter(start_date__lte=on_date, end_date__gte=on_date)
        .exclude(status__in=["باطل", "فسخ‌شده"])
        .order_by("-start_date")
        .first()
    )


def _money(value, label):
    if value in (None, ""):
        return None
    try:
        amount = Decimal(str(value).replace(",", ""))
    except InvalidOperation as exc:
        raise ValidationError(f"{label} باید عدد معتبر باشد.") from exc
    if amount < 0:
        raise ValidationError(f"{label} نمی‌تواند منفی باشد.")
    return amount


def overlapping_contract(space, start_date, end_date, *, exclude_pk=None):
    qs = Contract.objects.filter(
        space=space,
        start_date__lte=end_date,
        end_date__gte=start_date,
    )
    if exclude_pk:
        qs = qs.exclude(pk=exclude_pk)
    return qs.order_by("start_date", "pk").first()


def current_beneficiary_assignment(space, on_date):
    return (
        BeneficiaryAssignment.objects.filter(
            space=space,
            start_date__lte=on_date,
        )
        .filter(
            Q(end_date="") | Q(end_date__gte=on_date)
        )
        .order_by("-start_date", "-pk")
        .first()
    )


def _previous_jalali_day(value):
    import jdatetime
    year, month, day = (int(part) for part in value.split("/"))
    current = jdatetime.date(year, month, day).togregorian()
    return jdatetime.date.fromgregorian(date=current - timedelta(days=1)).strftime("%Y/%m/%d")


@retry_locked
@transaction.atomic
def assign_beneficiary(*, space, beneficiary, actor, start_date, basis="", termination_reason="", ip_address=None):
    try:
        start = normalize_jalali(start_date)
    except ValueError as exc:
        raise ValidationError("تاریخ شروع ارتباط معتبر نیست.") from exc
    if not start:
        raise ValidationError("تاریخ شروع ارتباط الزامی است.")

    existing = (
        BeneficiaryAssignment.objects.filter(space=space, start_date__lte=start)
        .filter(Q(end_date="") | Q(end_date__gte=start))
        .order_by("-start_date", "-pk")
        .first()
    )
    if existing and existing.beneficiary_id == beneficiary.pk:
        raise ValidationError("این بهره‌بردار در تاریخ انتخاب‌شده رابطه جاری با فضا دارد.")
    if existing and not termination_reason.strip():
        raise ValidationError("برای تغییر بهره‌بردار، علت خاتمه رابطه قبلی الزامی است.")

    if existing:
        previous_end = _previous_jalali_day(start)
        if existing.start_date and previous_end < existing.start_date:
            raise ValidationError("تاریخ شروع رابطه جدید باید پس از شروع رابطه جاری باشد.")
        existing.end_date = previous_end
        existing.status = BeneficiaryAssignment.Status.ENDED
        existing.termination_reason = termination_reason.strip()
        existing.save(update_fields=["end_date", "status", "termination_reason"])

    record = BeneficiaryAssignment.objects.create(
        space=space,
        beneficiary=beneficiary,
        role="بهره‌بردار",
        start_date=start,
        end_date="",
        status=BeneficiaryAssignment.Status.ACTIVE,
        basis=normalize_persian_text(basis),
        created_by=actor,
    )
    AuditEvent.objects.create(
        actor=actor,
        action="BENEFICIARY_ASSIGNMENT_CREATE",
        entity_type="BeneficiaryAssignment",
        entity_id=str(record.pk),
        reason=termination_reason.strip(),
        before={
            "beneficiary_id": existing.beneficiary_id,
            "assignment_id": existing.pk,
        } if existing else None,
        after={
            "space": space.code,
            "beneficiary_id": beneficiary.pk,
            "start_date": start,
            "basis": record.basis,
        },
        ip_address=ip_address,
    )
    TimelineEvent.objects.create(
        space=space,
        event_type="BENEFICIARY_CHANGE" if existing else "BENEFICIARY_ASSIGN",
        jalali_date=start,
        source_entity="BeneficiaryAssignment",
        source_entity_id=str(record.pk),
        title="تغییر بهره‌بردار" if existing else "ثبت بهره‌بردار",
        description=f"بهره‌بردار: {beneficiary.name}",
        previous_state=existing.beneficiary.name if existing else "",
        new_state=beneficiary.name,
        responsible_person=actor.get_full_name() or actor.username,
        provenance="ثبت دستی کنترل‌شده در سما",
        target_url=f"/spaces/{space.code}/",
    )
    return record


@retry_locked
@transaction.atomic
def create_contract(*, space, beneficiary, actor, values, ip_address=None):
    number = normalize_persian_text(values.get("number", ""))
    if not number:
        raise ValidationError("شماره قرارداد الزامی است.")
    if beneficiary is None:
        raise ValidationError("انتخاب بهره‌بردار ثبت‌شده الزامی است.")
    if Contract.objects.filter(number=number, space=space).exists():
        raise ValidationError("این شماره قرارداد برای فضا تکراری است.")

    try:
        signed = normalize_jalali(values.get("signed_date", ""))
        start = normalize_jalali(values.get("start_date", ""))
        end = normalize_jalali(values.get("end_date", ""))
    except ValueError as exc:
        raise ValidationError("تاریخ قرارداد معتبر نیست.") from exc
    if not start or not end or start > end:
        raise ValidationError("بازه تاریخ قرارداد معتبر نیست.")

    conflict = overlapping_contract(space, start, end)
    if conflict:
        raise ValidationError(
            f"این کد فضا در بازه انتخاب‌شده دارای قرارداد دیگری است: {conflict.number}"
        )

    assignment_at_start = (
        BeneficiaryAssignment.objects.filter(space=space, start_date__lte=start)
        .filter(Q(end_date="") | Q(end_date__gte=start))
        .order_by("-start_date", "-pk")
        .first()
    )
    if assignment_at_start and assignment_at_start.beneficiary_id != beneficiary.pk:
        raise ValidationError(
            "بهره‌بردار جاری فضا با قرارداد جدید متفاوت است؛ ابتدا تغییر بهره‌بردار را در پرونده فضا ثبت کنید."
        )

    record = Contract.objects.create(
        space=space,
        beneficiary=beneficiary,
        number=number,
        subject=normalize_persian_text(values.get("subject", "")),
        signed_date=signed,
        start_date=start,
        end_date=end,
        amount_rial=_money(values.get("amount_rial"), "مبلغ قرارداد"),
        investment_commitment_rial=_money(values.get("investment_commitment_rial"), "تعهد سرمایه‌گذاری"),
        status=normalize_persian_text(values.get("status", "")),
        signed_state=normalize_persian_text(values.get("signed_state", "")),
        notes=normalize_persian_text(values.get("notes", "")),
        is_historical=False,
        created_by=actor,
    )
    if assignment_at_start is None:
        BeneficiaryAssignment.objects.create(
            space=space,
            beneficiary=beneficiary,
            role="بهره‌بردار قرارداد",
            start_date=start,
            end_date=end,
            status=BeneficiaryAssignment.Status.ACTIVE,
            basis=f"قرارداد {number}",
            created_by=actor,
        )
    AuditEvent.objects.create(
        actor=actor,
        action="CONTRACT_CREATE",
        entity_type="Contract",
        entity_id=str(record.pk),
        after={
            "space": space.code,
            "number": number,
            "beneficiary_id": beneficiary.pk,
            "start_date": start,
            "end_date": end,
            "amount_rial": str(record.amount_rial) if record.amount_rial is not None else None,
        },
        ip_address=ip_address,
    )
    OperationalHistory.objects.create(
        entity_type="Contract",
        entity_id=str(record.pk),
        action="CREATED",
        new_state={"legal_status": record.status, "start_date": start, "end_date": end},
        responsible=actor,
    )
    TimelineEvent.objects.create(
        space=space,
        event_type="CONTRACT_CREATE",
        jalali_date=signed or start,
        source_entity="Contract",
        source_entity_id=str(record.pk),
        title=f"ثبت قرارداد {number}",
        description=f"بهره‌بردار: {beneficiary.name}",
        new_state=record.status,
        responsible_person=actor.get_full_name() or actor.username,
        provenance="ثبت دستی کنترل‌شده در سما",
        target_url=f"/spaces/{space.code}/",
    )
    return record


@retry_locked
@transaction.atomic
def add_amendment(*, contract, actor, values, ip_address=None):
    number = normalize_persian_text(values.get("number", ""))
    description = normalize_persian_text(values.get("description", ""))
    if not number or not description:
        raise ValidationError("شماره و شرح الحاقیه الزامی است.")
    if contract.amendments.filter(number=number).exists():
        raise ValidationError("شماره الحاقیه برای این قرارداد تکراری است.")
    try:
        date = normalize_jalali(values.get("effective_date", ""))
    except ValueError as exc:
        raise ValidationError("تاریخ الحاقیه معتبر نیست.") from exc
    if not date:
        raise ValidationError("تاریخ اثر الحاقیه الزامی است.")
    item = ContractAmendment.objects.create(
        contract=contract,
        number=number,
        effective_date=date,
        description=description,
        amount_change_rial=_money(values.get("amount_change_rial"), "تغییر مبلغ"),
    )
    AuditEvent.objects.create(
        actor=actor,
        action="CONTRACT_AMENDMENT_CREATE",
        entity_type="ContractAmendment",
        entity_id=str(item.pk),
        after={"contract": contract.pk, "number": number, "effective_date": date},
        ip_address=ip_address,
    )
    TimelineEvent.objects.create(
        space=contract.space,
        event_type="CONTRACT_AMENDMENT",
        jalali_date=date,
        source_entity="ContractAmendment",
        source_entity_id=str(item.pk),
        title=f"الحاقیه {number}",
        description=description,
        responsible_person=actor.get_full_name() or actor.username,
        provenance="ثبت دستی کنترل‌شده در سما",
        target_url=f"/spaces/{contract.space.code}/",
    )
    return item
