from decimal import Decimal, ROUND_HALF_UP

from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from domains.identity.models import AuditEvent
from domains.operations.models import (
    ElectricityAllocation,
    ElectricityBill,
    ElectricityCalculationSnapshot,
    UtilityMeasurement, UtilityParameterRule,
)
from services.database import retry_locked
from services.dates import normalize_jalali


ZERO = Decimal("0")
HUNDRED = Decimal("100")
PERCENT_QUANT = Decimal("0.0001")
RIAL = Decimal("1")


def _date(value, *, required=True):
    raw = (value or "").strip()
    if not raw and not required:
        return ""
    try:
        result = normalize_jalali(raw)
    except ValueError as exc:
        raise ValidationError("تاریخ شمسی معتبر نیست.") from exc
    if required and not result:
        raise ValidationError("تاریخ الزامی است.")
    return result


def _decimal(value, label, *, allow_null=False, min_value=ZERO, max_value=None):
    if value in (None, ""):
        if allow_null:
            return None
        raise ValidationError(f"{label} الزامی است.")
    try:
        result = Decimal(str(value).replace(",", "").strip())
    except Exception as exc:
        raise ValidationError(f"{label} باید عدد معتبر باشد.") from exc
    if result < min_value:
        raise ValidationError(f"{label} نمی‌تواند کمتر از {min_value} باشد.")
    if max_value is not None and result > max_value:
        raise ValidationError(f"{label} نمی‌تواند بیشتر از {max_value} باشد.")
    return result


def _ensure_bill_mutable(bill):
    if bill.status == ElectricityBill.Status.FINAL:
        raise ValidationError("قبض نهایی مستقیم قابل ویرایش نیست؛ ابتدا باید با علت بازگشایی شود.")


@retry_locked
@transaction.atomic
def create_electricity_bill(*, unit, actor, values, document=None, ip_address=None):
    period_start = _date(values.get("period_start"))
    period_end = _date(values.get("period_end"))
    if period_start > period_end:
        raise ValidationError("پایان دوره نمی‌تواند قبل از شروع دوره باشد.")
    beneficiary_share = _decimal(values.get("beneficiary_share_percent"), "درصد سهم بهره‌برداران", max_value=HUNDRED)
    organization_share = _decimal(values.get("organization_share_percent"), "درصد سهم سازمان", max_value=HUNDRED)
    if beneficiary_share + organization_share != HUNDRED:
        raise ValidationError("جمع سهم بهره‌برداران و سازمان باید دقیقاً ۱۰۰٪ باشد.")
    if ElectricityBill.objects.filter(unit=unit, period_start=period_start, period_end=period_end).exists():
        raise ValidationError("برای این واحد و دوره قبلاً قبض برق ثبت شده است.")

    bill = ElectricityBill.objects.create(
        unit=unit,
        period_start=period_start,
        period_end=period_end,
        bill_date=_date(values.get("bill_date"), required=False),
        amount_rial=_decimal(values.get("amount_rial"), "مبلغ قبض"),
        beneficiary_share_percent=beneficiary_share,
        organization_share_percent=organization_share,
        status=ElectricityBill.Status.DRAFT,
        notes=(values.get("notes") or "").strip(),
        supporting_document=document,
        created_by=actor,
    )
    AuditEvent.objects.create(
        actor=actor,
        action="ELECTRICITY_BILL_CREATE",
        entity_type="ElectricityBill",
        entity_id=str(bill.pk),
        after={
            "code": bill.sama_code,
            "unit_id": unit.pk,
            "period_start": bill.period_start,
            "period_end": bill.period_end,
            "amount_rial": str(bill.amount_rial),
            "beneficiary_share_percent": str(bill.beneficiary_share_percent),
            "organization_share_percent": str(bill.organization_share_percent),
        },
        ip_address=ip_address,
    )
    return bill


@retry_locked
@transaction.atomic
def update_electricity_bill(*, bill, actor, values, reason, ip_address=None):
    _ensure_bill_mutable(bill)
    if not actor.is_staff:
        raise PermissionDenied("ویرایش مبلغ و درصدهای قبض فقط برای کاربر مجاز امکان‌پذیر است.")
    reason = (reason or "").strip()
    if not reason:
        raise ValidationError("علت اصلاح قبض الزامی است.")

    amount = _decimal(values.get("amount_rial"), "مبلغ قبض")
    beneficiary_share = _decimal(values.get("beneficiary_share_percent"), "درصد سهم بهره‌برداران", max_value=HUNDRED)
    organization_share = _decimal(values.get("organization_share_percent"), "درصد سهم سازمان", max_value=HUNDRED)
    if beneficiary_share + organization_share != HUNDRED:
        raise ValidationError("جمع سهم بهره‌برداران و سازمان باید دقیقاً ۱۰۰٪ باشد.")

    before = {
        "amount_rial": str(bill.amount_rial),
        "beneficiary_share_percent": str(bill.beneficiary_share_percent),
        "organization_share_percent": str(bill.organization_share_percent),
        "status": bill.status,
    }
    bill.amount_rial = amount
    bill.beneficiary_share_percent = beneficiary_share
    bill.organization_share_percent = organization_share
    bill.notes = (values.get("notes") or bill.notes or "").strip()
    bill.save(update_fields=[
        "amount_rial", "beneficiary_share_percent", "organization_share_percent",
        "notes", "updated_at",
    ])
    recalculate_electricity_bill(bill=bill, actor=actor, ip_address=ip_address)
    bill.refresh_from_db()
    AuditEvent.objects.create(
        actor=actor,
        action="ELECTRICITY_BILL_UPDATE",
        entity_type="ElectricityBill",
        entity_id=str(bill.pk),
        reason=reason,
        before=before,
        after={
            "amount_rial": str(bill.amount_rial),
            "beneficiary_share_percent": str(bill.beneficiary_share_percent),
            "organization_share_percent": str(bill.organization_share_percent),
            "status": bill.status,
        },
        ip_address=ip_address,
    )
    return bill


@retry_locked
@transaction.atomic
def record_measurement(*, space, actor, values, ip_address=None):
    period_start = _date(values.get("period_start"))
    period_end = _date(values.get("period_end"))
    reading_date = _date(values.get("reading_date"))
    if period_start > period_end:
        raise ValidationError("پایان دوره اندازه‌گیری نمی‌تواند قبل از شروع آن باشد.")
    utility_type = values.get("utility_type", UtilityMeasurement.Type.ELECTRICITY)
    if utility_type not in UtilityMeasurement.Type.values:
        raise ValidationError("نوع انشعاب معتبر نیست.")
    measurement = UtilityMeasurement.objects.create(
        space=space,
        utility_type=utility_type,
        period_start=period_start,
        period_end=period_end,
        consumption=_decimal(values.get("consumption"), "مقدار مصرف"),
        reading_date=reading_date,
        meter_number=(values.get("meter_number") or "").strip(),
        measurement_unit=(values.get("measurement_unit") or "kWh").strip(),
        source=(values.get("source") or "").strip(),
        is_submeter=values.get("is_submeter") in (True, "1", "on"),
        is_valid=values.get("is_valid", True) in (True, "1", "on"),
        notes=(values.get("notes") or "").strip(),
        created_by=actor,
    )
    AuditEvent.objects.create(
        actor=actor,
        action="UTILITY_MEASUREMENT_CREATE",
        entity_type="UtilityMeasurement",
        entity_id=str(measurement.pk),
        after={
            "space": space.code,
            "utility_type": utility_type,
            "consumption": str(measurement.consumption),
            "reading_date": reading_date,
            "is_submeter": measurement.is_submeter,
            "is_valid": measurement.is_valid,
        },
        ip_address=ip_address,
    )
    return measurement


@retry_locked
@transaction.atomic
def upsert_electricity_allocation(*, bill, space, actor, values, ip_address=None):
    _ensure_bill_mutable(bill)
    measurement = values.get("measurement")
    if measurement:
        if measurement.space_id != space.pk or measurement.utility_type != UtilityMeasurement.Type.ELECTRICITY:
            raise ValidationError("Measurement انتخاب‌شده متعلق به این فضای تجاری و برق نیست.")
        if not measurement.is_valid:
            raise ValidationError("Measurement نامعتبر نمی‌تواند مبنای محاسبه برق باشد.")
        if measurement.period_start > bill.period_end or measurement.period_end < bill.period_start:
            raise ValidationError("دوره Measurement با دوره قبض برق هم‌پوشانی ندارد.")

    override = _decimal(
        values.get("manual_override_percent"),
        "سهم Override",
        allow_null=True,
        max_value=HUNDRED,
    )
    override_reason = (values.get("override_reason") or "").strip()
    if override is not None and not actor.is_staff:
        raise PermissionDenied("اصلاح دستی درصد سهم فقط برای کاربر مجاز امکان‌پذیر است.")
    if override is not None and not override_reason:
        raise ValidationError("برای سهم دستی، ثبت علت Override الزامی است.")

    defaults = {
        "eligible": values.get("eligible", True) in (True, "1", "on"),
        "category": values.get("category"),
        "effective_area": _decimal(values.get("effective_area"), "متراژ مؤثر", allow_null=True),
        "eui": _decimal(values.get("eui"), "EUI", allow_null=True),
        "operational_factor": _decimal(values.get("operational_factor"), "ضریب بهره‌برداری", allow_null=True),
        "special_consumption": _decimal(values.get("special_consumption"), "مصرف ویژه", allow_null=True),
        "measurement": measurement,
        "manual_override_percent": override,
        "override_reason": override_reason,
        "notes": (values.get("notes") or "").strip(),
        "created_by": actor,
    }
    allocation, created = ElectricityAllocation.objects.get_or_create(
        bill=bill,
        space=space,
        defaults={
            **defaults,
            "calculated_share_percent": None,
            "final_share_percent": ZERO,
            "calculation_source": ElectricityAllocation.Source.APPROVED_MODEL,
            "confidence_level": ElectricityAllocation.Confidence.INCOMPLETE,
        },
    )
    before = None
    if not created:
        before = {
            "eligible": allocation.eligible,
            "category_id": allocation.category_id,
            "effective_area": str(allocation.effective_area) if allocation.effective_area is not None else None,
            "eui": str(allocation.eui) if allocation.eui is not None else None,
            "operational_factor": str(allocation.operational_factor) if allocation.operational_factor is not None else None,
            "special_consumption": str(allocation.special_consumption) if allocation.special_consumption is not None else None,
            "measurement_id": allocation.measurement_id,
            "manual_override_percent": str(allocation.manual_override_percent) if allocation.manual_override_percent is not None else None,
        }
        for key, value in defaults.items():
            setattr(allocation, key, value)
        allocation.save()

    recalculate_electricity_bill(bill=bill, actor=actor, ip_address=ip_address)
    allocation.refresh_from_db()
    AuditEvent.objects.create(
        actor=actor,
        action="ELECTRICITY_ALLOCATION_CREATE" if created else "ELECTRICITY_ALLOCATION_UPDATE",
        entity_type="ElectricityAllocation",
        entity_id=str(allocation.pk),
        before=before,
        after={
            "bill_id": bill.pk,
            "space": space.code,
            "calculated_share_percent": str(allocation.calculated_share_percent) if allocation.calculated_share_percent is not None else None,
            "manual_override_percent": str(allocation.manual_override_percent) if allocation.manual_override_percent is not None else None,
            "final_share_percent": str(allocation.final_share_percent),
            "source": allocation.calculation_source,
            "confidence": allocation.confidence_level,
        },
        reason=override_reason,
        ip_address=ip_address,
    )
    return allocation


def _allocation_weight(allocation):
    measurement = allocation.measurement
    if measurement and measurement.is_valid:
        source = ElectricityAllocation.Source.SUBMETER if measurement.is_submeter else ElectricityAllocation.Source.MEASUREMENT
        return measurement.consumption, source, ElectricityAllocation.Confidence.REAL_MEASUREMENT

    if allocation.special_consumption is not None:
        return allocation.special_consumption, ElectricityAllocation.Source.EQUIPMENT, ElectricityAllocation.Confidence.VALID_EQUIPMENT

    eui = allocation.eui
    if eui is None and allocation.category_id and allocation.category.eui is not None:
        eui = allocation.category.eui
    if allocation.effective_area is not None and eui is not None:
        factor = allocation.operational_factor if allocation.operational_factor is not None else Decimal("1")
        weight = allocation.effective_area * eui * factor
        return weight, ElectricityAllocation.Source.APPROVED_MODEL, ElectricityAllocation.Confidence.APPROVED_MODEL

    return None, ElectricityAllocation.Source.APPROVED_MODEL, ElectricityAllocation.Confidence.INCOMPLETE


@retry_locked
@transaction.atomic
def recalculate_electricity_bill(*, bill, actor, ip_address=None):
    _ensure_bill_mutable(bill)
    allocations = list(
        bill.allocations.select_related("category", "measurement", "space").order_by("space__code", "pk")
    )
    eligible = [item for item in allocations if item.eligible]
    weighted = []
    incomplete = False
    for item in eligible:
        weight, source, confidence = _allocation_weight(item)
        if weight is None:
            incomplete = True
        elif weight < ZERO:
            raise ValidationError("وزن مصرف نمی‌تواند منفی باشد.")
        weighted.append((item, weight, source, confidence))

    total_weight = sum((weight for _, weight, _, _ in weighted if weight is not None), ZERO)
    if eligible and total_weight == ZERO:
        incomplete = True

    calculated_running = ZERO
    for index, (item, weight, source, confidence) in enumerate(weighted):
        if weight is None or total_weight == ZERO:
            calculated = None
        elif index == max((pos for pos, row in enumerate(weighted) if row[1] is not None), default=-1):
            calculated = bill.beneficiary_share_percent - calculated_running
        else:
            calculated = (
                bill.beneficiary_share_percent * weight / total_weight
            ).quantize(PERCENT_QUANT, rounding=ROUND_HALF_UP)
            calculated_running += calculated
        item.calculated_share_percent = calculated
        if item.manual_override_percent is not None:
            item.final_share_percent = item.manual_override_percent
            item.calculation_source = ElectricityAllocation.Source.MANUAL_OVERRIDE
            item.confidence_level = confidence if confidence != ElectricityAllocation.Confidence.INCOMPLETE else ElectricityAllocation.Confidence.REVIEW
        else:
            item.final_share_percent = calculated if calculated is not None else ZERO
            item.calculation_source = source
            item.confidence_level = confidence
        item.payable_amount_rial = None
        item.save(update_fields=[
            "calculated_share_percent", "final_share_percent", "calculation_source",
            "confidence_level", "payable_amount_rial", "updated_at",
        ])

    for item in allocations:
        if not item.eligible:
            item.calculated_share_percent = ZERO
            item.final_share_percent = item.manual_override_percent if item.manual_override_percent is not None else ZERO
            item.payable_amount_rial = None
            item.save(update_fields=["calculated_share_percent", "final_share_percent", "payable_amount_rial", "updated_at"])

    final_sum = sum((item.final_share_percent for item in eligible), ZERO)
    percent_ok = final_sum == bill.beneficiary_share_percent
    if incomplete or not percent_ok:
        bill.status = ElectricityBill.Status.REVIEW_REQUIRED
        for item in allocations:
            item.payable_amount_rial = None
            item.save(update_fields=["payable_amount_rial", "updated_at"])
    else:
        organization_amount = bill.organization_amount_rial
        beneficiary_pool = bill.amount_rial - organization_amount
        allocated = ZERO
        eligible_ordered = [item for item in allocations if item.eligible]
        for index, item in enumerate(eligible_ordered):
            if index == len(eligible_ordered) - 1:
                amount = beneficiary_pool - allocated
            else:
                amount = (
                    bill.amount_rial * item.final_share_percent / HUNDRED
                ).quantize(RIAL, rounding=ROUND_HALF_UP)
                allocated += amount
            item.payable_amount_rial = amount
            item.save(update_fields=["payable_amount_rial", "updated_at"])
        bill.status = ElectricityBill.Status.CALCULATED

    bill.save(update_fields=["status", "updated_at"])
    AuditEvent.objects.create(
        actor=actor,
        action="ELECTRICITY_RECALCULATE",
        entity_type="ElectricityBill",
        entity_id=str(bill.pk),
        after={
            "status": bill.status,
            "beneficiary_share_percent": str(bill.beneficiary_share_percent),
            "final_space_share_sum": str(final_sum),
            "allocation_count": len(eligible),
            "incomplete": incomplete,
        },
        ip_address=ip_address,
    )
    return bill


def _snapshot_payload(bill):
    allocations = []
    for item in bill.allocations.select_related("space", "measurement", "category").order_by("space__code", "pk"):
        allocations.append({
            "space_code": item.space.code,
            "eligible": item.eligible,
            "category": item.category.name if item.category_id else None,
            "effective_area": str(item.effective_area) if item.effective_area is not None else None,
            "eui": str(item.eui) if item.eui is not None else None,
            "operational_factor": str(item.operational_factor) if item.operational_factor is not None else None,
            "special_consumption": str(item.special_consumption) if item.special_consumption is not None else None,
            "measurement_id": item.measurement_id,
            "calculated_share_percent": str(item.calculated_share_percent) if item.calculated_share_percent is not None else None,
            "manual_override_percent": str(item.manual_override_percent) if item.manual_override_percent is not None else None,
            "final_share_percent": str(item.final_share_percent),
            "payable_amount_rial": str(item.payable_amount_rial) if item.payable_amount_rial is not None else None,
            "calculation_source": item.calculation_source,
            "confidence_level": item.confidence_level,
            "override_reason": item.override_reason,
        })
    rules = []
    effective_rules = UtilityParameterRule.objects.filter(
        active=True,
        effective_from__lte=bill.period_end,
    ).filter(
        Q(effective_to="") | Q(effective_to__gte=bill.period_start)
    ).order_by("key", "-effective_from", "-id")
    seen = set()
    for rule in effective_rules:
        if rule.key in seen:
            continue
        seen.add(rule.key)
        rules.append({
            "key": rule.key,
            "label": rule.label,
            "value_decimal": str(rule.value_decimal) if rule.value_decimal is not None else None,
            "value_text": rule.value_text,
            "unit": rule.unit,
            "effective_from": rule.effective_from,
            "effective_to": rule.effective_to,
        })
    return {
        "bill": {
            "code": bill.sama_code,
            "unit_id": bill.unit_id,
            "period_start": bill.period_start,
            "period_end": bill.period_end,
            "amount_rial": str(bill.amount_rial),
            "beneficiary_share_percent": str(bill.beneficiary_share_percent),
            "organization_share_percent": str(bill.organization_share_percent),
            "organization_amount_rial": str(bill.organization_amount_rial),
        },
        "allocations": allocations,
        "effective_rules": rules,
    }


@retry_locked
@transaction.atomic
def finalize_electricity_bill(*, bill, actor, ip_address=None):
    if bill.status == ElectricityBill.Status.FINAL:
        raise ValidationError("این قبض قبلاً نهایی شده است.")
    recalculate_electricity_bill(bill=bill, actor=actor, ip_address=ip_address)
    bill.refresh_from_db()
    if bill.status != ElectricityBill.Status.CALCULATED:
        raise ValidationError("قبض تا رفع مغایرت درصدها و داده‌های ناقص قابل نهایی‌سازی نیست.")
    if not bill.allocations.filter(eligible=True).exists():
        raise ValidationError("قبض بدون فضای مشمول قابل نهایی‌سازی نیست.")

    version = (bill.snapshots.order_by("-version").values_list("version", flat=True).first() or 0) + 1
    snapshot = ElectricityCalculationSnapshot.objects.create(
        bill=bill,
        version=version,
        payload=_snapshot_payload(bill),
        created_by=actor,
    )
    bill.status = ElectricityBill.Status.FINAL
    bill.finalized_at = timezone.now()
    bill.finalized_by = actor
    bill.reopen_reason = ""
    bill.save(update_fields=["status", "finalized_at", "finalized_by", "reopen_reason", "updated_at"])
    AuditEvent.objects.create(
        actor=actor,
        action="ELECTRICITY_FINALIZE",
        entity_type="ElectricityBill",
        entity_id=str(bill.pk),
        after={"status": bill.status, "snapshot_id": snapshot.pk, "version": version},
        ip_address=ip_address,
    )
    return snapshot


@retry_locked
@transaction.atomic
def reopen_electricity_bill(*, bill, actor, reason, ip_address=None):
    if not actor.is_staff:
        raise PermissionDenied("بازگشایی محاسبه نهایی فقط برای کاربر مجاز امکان‌پذیر است.")
    if bill.status != ElectricityBill.Status.FINAL:
        raise ValidationError("فقط قبض نهایی قابل بازگشایی است.")
    reason = (reason or "").strip()
    if not reason:
        raise ValidationError("علت بازگشایی الزامی است.")
    bill.status = ElectricityBill.Status.REOPENED
    bill.reopen_reason = reason
    bill.save(update_fields=["status", "reopen_reason", "updated_at"])
    AuditEvent.objects.create(
        actor=actor,
        action="ELECTRICITY_REOPEN",
        entity_type="ElectricityBill",
        entity_id=str(bill.pk),
        reason=reason,
        before={"status": ElectricityBill.Status.FINAL},
        after={"status": bill.status},
        ip_address=ip_address,
    )
    return bill
