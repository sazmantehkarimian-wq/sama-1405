from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP

from django.db import transaction

from .models import UtilityAllocation, UtilityAllocationPolicy, UtilityBill, UtilitySpaceProfile


ZERO = Decimal("0")
ONE = Decimal("1")
HUNDRED = Decimal("100")
PERCENT_Q = Decimal("0.00000001")
RIAL_Q = Decimal("1")


@dataclass(frozen=True)
class AllocationLine:
    profile_id: int
    space_code: str
    basis: str
    weight: Decimal
    share_percent: Decimal
    amount_rial: Decimal
    manual: bool


@dataclass(frozen=True)
class AllocationResult:
    beneficiary_percent: Decimal
    organization_percent: Decimal
    beneficiary_amount_rial: Decimal
    organization_amount_rial: Decimal
    lines: tuple[AllocationLine, ...]


def _d(value, default=ZERO):
    if value is None:
        return default
    return Decimal(str(value))


def method3_weight(profile: UtilitySpaceProfile, season_factor: Decimal) -> Decimal:
    """روش سوم: مصرف متراژی تعدیل‌شده + مصرف ویژه تجهیزات."""
    area = _d(profile.effective_area)
    eui = _d(profile.eui)
    hours = _d(profile.hours_factor, ONE)
    category = _d(profile.category_factor, ONE)
    row = _d(profile.row_factor, ONE)
    season = _d(season_factor, ONE)
    special = _d(profile.special_consumption)
    return max(ZERO, area * eui * hours * category * row * season + special)


def _effective_policy(policy: UtilityAllocationPolicy, fixed_manual: Decimal) -> tuple[Decimal, Decimal]:
    beneficiary = _d(policy.beneficiary_percent)
    organization = _d(policy.organization_percent)
    if beneficiary == ZERO and organization == ZERO:
        return ZERO, ZERO
    if fixed_manual > HUNDRED:
        raise ValueError("مجموع درصدهای دستی از ۱۰۰٪ بیشتر است.")
    if fixed_manual > beneficiary:
        beneficiary = fixed_manual
        organization = HUNDRED - beneficiary
    return beneficiary, organization


def calculate_bill(bill: UtilityBill, persist=True) -> AllocationResult:
    policy = bill.account.allocation_policy
    profiles = list(bill.account.space_profiles.select_related("space").filter(included=True).order_by("space__code", "id"))
    readings = {r.profile_id: r for r in bill.meter_readings.filter(is_valid=True).select_related("profile")}

    fixed_manual = sum(
        (_d(p.manual_share_percent) for p in profiles if p.manual_share_percent is not None and p.manual_share_locked),
        ZERO,
    )
    beneficiary_percent, organization_percent = _effective_policy(policy, fixed_manual)
    if beneficiary_percent == ZERO and organization_percent == ZERO:
        raise ValueError("سهم سازمان و بهره‌بردار هنوز تعیین نشده است؛ وضعیت ۰/۰ قابل ثبت است اما قابل محاسبه نیست.")
    remaining_percent = max(ZERO, beneficiary_percent - fixed_manual)

    weighted = []
    for p in profiles:
        manual = p.manual_share_percent is not None and p.manual_share_locked
        if manual:
            weighted.append((p, UtilityAllocation.Basis.MANUAL, ZERO, _d(p.manual_share_percent), True))
            continue
        reading = readings.get(p.id)
        if reading is not None:
            weight = _d(reading.measured_consumption)
            basis = UtilityAllocation.Basis.MEASURED
        else:
            weight = method3_weight(p, _d(policy.season_factor, ONE))
            basis = UtilityAllocation.Basis.EQUIPMENT if _d(p.special_consumption) > ZERO else UtilityAllocation.Basis.METHOD3
        weighted.append((p, basis, weight, None, False))

    auto_weight_sum = sum((row[2] for row in weighted if not row[4]), ZERO)
    auto_rows = [row for row in weighted if not row[4]]
    if remaining_percent > ZERO and not auto_rows:
        raise ValueError("بخشی از سهم بهره‌بردار بدون کدفضای خودکار باقی مانده است.")
    if remaining_percent > ZERO and auto_weight_sum <= ZERO:
        raise ValueError("برای توزیع سهم باقی‌مانده، وزن مصرف معتبر وجود ندارد.")

    raw_lines = []
    for p, basis, weight, manual_share, is_manual in weighted:
        if is_manual:
            share = manual_share
        elif remaining_percent == ZERO:
            share = ZERO
        else:
            share = (remaining_percent * weight / auto_weight_sum) if auto_weight_sum else ZERO
        raw_lines.append((p, basis, weight, share, is_manual))

    total_amount = _d(bill.amount_rial)
    organization_amount = (total_amount * organization_percent / HUNDRED).quantize(RIAL_Q, rounding=ROUND_HALF_UP)
    beneficiary_target = total_amount - organization_amount

    lines = []
    allocated = ZERO
    nonzero_indexes = [i for i, row in enumerate(raw_lines) if row[3] > ZERO]
    last_index = nonzero_indexes[-1] if nonzero_indexes else None
    for i, (p, basis, weight, share, is_manual) in enumerate(raw_lines):
        share = share.quantize(PERCENT_Q, rounding=ROUND_HALF_UP)
        if i == last_index:
            amount = beneficiary_target - allocated
        else:
            amount = (total_amount * share / HUNDRED).quantize(RIAL_Q, rounding=ROUND_HALF_UP)
            allocated += amount
        lines.append(AllocationLine(profile_id=p.id, space_code=p.space.code, basis=basis, weight=weight, share_percent=share, amount_rial=amount, manual=is_manual))

    beneficiary_amount = sum((line.amount_rial for line in lines), ZERO)
    if beneficiary_amount + organization_amount != total_amount:
        raise AssertionError("کنترل نهایی قبض برقرار نیست.")

    result = AllocationResult(
        beneficiary_percent=beneficiary_percent,
        organization_percent=organization_percent,
        beneficiary_amount_rial=beneficiary_amount,
        organization_amount_rial=organization_amount,
        lines=tuple(lines),
    )
    if persist:
        _persist_result(bill, policy, profiles, result)
    return result


@transaction.atomic
def _persist_result(bill, policy, profiles, result):
    profile_by_id = {p.id: p for p in profiles}
    bill.allocations.all().delete()
    UtilityAllocation.objects.bulk_create([
        UtilityAllocation(
            bill=bill,
            profile=profile_by_id[line.profile_id],
            basis=line.basis,
            consumption_weight=line.weight,
            share_percent=line.share_percent,
            amount_rial=line.amount_rial,
            overridden=line.manual,
            snapshot={"space_code": line.space_code, "method": policy.method, "manual_locked": line.manual},
        ) for line in result.lines
    ])
    bill.beneficiary_percent_effective = result.beneficiary_percent
    bill.organization_percent_effective = result.organization_percent
    bill.beneficiary_amount_rial = result.beneficiary_amount_rial
    bill.organization_amount_rial = result.organization_amount_rial
    bill.status = UtilityBill.Status.CALCULATED
    bill.calculation_snapshot = {
        "method": policy.method,
        "priority": ["MEASURED", "EQUIPMENT", "METHOD3"],
        "beneficiary_percent_effective": str(result.beneficiary_percent),
        "organization_percent_effective": str(result.organization_percent),
        "control_total_rial": str(result.beneficiary_amount_rial + result.organization_amount_rial),
    }
    bill.save(update_fields=[
        "beneficiary_percent_effective", "organization_percent_effective",
        "beneficiary_amount_rial", "organization_amount_rial", "status",
        "calculation_snapshot", "updated_at",
    ])
