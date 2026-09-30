"""Transactional operational commands shared by UI and future API callers."""
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from domains.identity.models import AuditEvent
from domains.operations.models import Appraisal, AppraisalFee, UtilityRecord, WorkflowInstance
from services.dates import normalize_jalali


def _date(value: str, *, required: bool = False) -> str:
    value = (value or "").strip()
    if not value and not required:
        return ""
    try:
        return normalize_jalali(value)
    except ValueError as exc:
        raise ValidationError("تاریخ شمسی معتبر نیست.") from exc


def _money(value: str, label: str, *, allow_zero: bool = False) -> Decimal:
    try:
        amount = Decimal(str(value).replace(",", "").strip())
    except Exception as exc:
        raise ValidationError(f"{label} باید عدد معتبر باشد.") from exc
    if amount < 0 or (not allow_zero and amount == 0):
        raise ValidationError(f"{label} باید بزرگ‌تر از صفر باشد.")
    return amount


@transaction.atomic
def record_appraisal_fee(*, appraisal: Appraisal, actor, amount: str, payment_status: str,
                         payment_date: str = "", payment_reference: str = "",
                         follow_up_date: str = "", notes: str = "", ip_address=None) -> AppraisalFee:
    if hasattr(appraisal, "fee"):
        raise ValidationError("برای این کارشناسی قبلاً پرونده حق‌الزحمه ثبت شده است.")
    fee = AppraisalFee.objects.create(
        appraisal=appraisal, amount_rial=_money(amount, "حق‌الزحمه"),
        payment_status=payment_status.strip(), payment_date=_date(payment_date),
        payment_reference=payment_reference.strip(), follow_up_date=_date(follow_up_date), notes=notes.strip(),
    )
    AuditEvent.objects.create(actor=actor, action="APPRAISAL_FEE_CREATE", entity_type="AppraisalFee",
                              entity_id=str(fee.pk), after={"space": appraisal.space.code,
                              "amount_rial": str(fee.amount_rial), "payment_status": fee.payment_status},
                              ip_address=ip_address)
    return fee


@transaction.atomic
def record_utility(*, space, actor, values: dict, ip_address=None) -> UtilityRecord:
    utility_type = values.get("utility_type", "")
    if utility_type not in UtilityRecord.Type.values:
        raise ValidationError("نوع انشعاب معتبر نیست.")
    bill = _money(values.get("bill_amount_rial", ""), "مبلغ قبض", allow_zero=True)
    organization = _money(values.get("organization_share_rial", ""), "سهم سازمان", allow_zero=True)
    beneficiary = _money(values.get("beneficiary_share_rial", ""), "سهم بهره‌بردار", allow_zero=True)
    if organization + beneficiary != bill:
        raise ValidationError("جمع سهم سازمان و بهره‌بردار باید با مبلغ قبض برابر باشد.")
    overridden = values.get("overridden") in (True, "on", "1")
    reason = values.get("override_reason", "").strip()
    if overridden and not reason:
        raise ValidationError("ثبت علت برای محاسبه اصلاح‌شده الزامی است.")
    record = UtilityRecord.objects.create(
        space=space, utility_type=utility_type, account_number=values.get("account_number", "").strip(),
        period_start=_date(values.get("period_start", ""), required=True),
        period_end=_date(values.get("period_end", ""), required=True),
        consumption=Decimal(values["consumption"]) if values.get("consumption", "").strip() else None,
        bill_amount_rial=bill, organization_share_rial=organization, beneficiary_share_rial=beneficiary,
        calculation_basis=values.get("calculation_basis", "").strip(), overridden=overridden,
        override_reason=reason, payment_status=values.get("payment_status", "").strip(),
        payment_date=_date(values.get("payment_date", "")),
    )
    AuditEvent.objects.create(actor=actor, action="UTILITY_RECORD_CREATE", entity_type="UtilityRecord",
                              entity_id=str(record.pk), after={"space": space.code, "bill_amount_rial": str(bill),
                              "overridden": overridden}, ip_address=ip_address)
    return record


@transaction.atomic
def transition_workflow(*, workflow: WorkflowInstance, actor, new_state: str, next_action: str,
                        due_date: str = "", ip_address=None) -> WorkflowInstance:
    if workflow.state != WorkflowInstance.State.OPEN:
        raise ValidationError("فرایند بسته‌شده قابل تغییر نیست.")
    if new_state not in WorkflowInstance.State.values:
        raise ValidationError("وضعیت فرایند معتبر نیست.")
    before = {"state": workflow.state, "next_action": workflow.next_action, "due_date": workflow.due_date}
    workflow.state = new_state
    workflow.next_action = next_action.strip()
    workflow.due_date = _date(due_date)
    if new_state in (WorkflowInstance.State.DONE, WorkflowInstance.State.CANCELLED):
        workflow.closed_at = timezone.now()
    workflow.save(update_fields=["state", "next_action", "due_date", "closed_at"])
    AuditEvent.objects.create(actor=actor, action="WORKFLOW_TRANSITION", entity_type="WorkflowInstance",
                              entity_id=str(workflow.pk), before=before,
                              after={"state": workflow.state, "next_action": workflow.next_action,
                                     "due_date": workflow.due_date}, ip_address=ip_address)
    return workflow
