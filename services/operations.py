"""Transactional operational commands shared by UI and future API callers."""
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from domains.identity.models import AuditEvent
from domains.documents.models import Document
from domains.operations.models import (
    Alert, Appraisal, AppraisalFee, CommissionDecision, OperationalHistory,
    TimelineEvent, UtilityRecord, WorkflowInstance,
)
from services.dates import normalize_jalali
from services.database import retry_locked


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


@retry_locked
@transaction.atomic
def record_appraisal_fee(*, appraisal: Appraisal, actor, amount: str, payment_status: str,
                         payment_date: str = "", payment_reference: str = "",
                         follow_up_date: str = "", notes: str = "", document: Document | None = None,
                         ip_address=None) -> AppraisalFee:
    if hasattr(appraisal, "fee"):
        raise ValidationError("برای این کارشناسی قبلاً پرونده حق‌الزحمه ثبت شده است.")
    fee = AppraisalFee.objects.create(
        appraisal=appraisal, amount_rial=_money(amount, "حق‌الزحمه"),
        payment_status=payment_status.strip(), payment_date=_date(payment_date),
        payment_reference=payment_reference.strip(), follow_up_date=_date(follow_up_date), notes=notes.strip(),
        supporting_document=document,
    )
    AuditEvent.objects.create(actor=actor, action="APPRAISAL_FEE_CREATE", entity_type="AppraisalFee",
                              entity_id=str(fee.pk), after={"space": appraisal.space.code,
                              "amount_rial": str(fee.amount_rial), "payment_status": fee.payment_status},
                              ip_address=ip_address)
    OperationalHistory.objects.create(entity_type="AppraisalFee", entity_id=str(fee.pk),
        action="CREATED", previous_state=None, new_state={"payment_status": fee.payment_status},
        responsible=actor)
    return fee


@retry_locked
@transaction.atomic
def record_utility(*, space, actor, values: dict, document: Document | None = None, ip_address=None) -> UtilityRecord:
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
        payment_date=_date(values.get("payment_date", "")), supporting_document=document,
    )
    AuditEvent.objects.create(actor=actor, action="UTILITY_RECORD_CREATE", entity_type="UtilityRecord",
                              entity_id=str(record.pk), after={"space": space.code, "bill_amount_rial": str(bill),
                              "overridden": overridden}, ip_address=ip_address)
    OperationalHistory.objects.create(entity_type="UtilityRecord", entity_id=str(record.pk),
        action="CREATED", previous_state=None, new_state={"payment_status": record.payment_status,
        "bill_amount_rial": str(bill)}, reason=reason, responsible=actor)
    return record


@retry_locked
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
    OperationalHistory.objects.create(entity_type="WorkflowInstance", entity_id=str(workflow.pk),
        action="TRANSITION", previous_state=before,
        new_state={"state": workflow.state, "next_action": workflow.next_action, "due_date": workflow.due_date},
        responsible=actor)
    return workflow


@retry_locked
@transaction.atomic
def create_workflow(*, space, actor, process_type: str, title: str, next_action: str,
                    due_date: str = "", ip_address=None) -> WorkflowInstance:
    allowed = {"CONTRACT", "APPRAISAL", "AUCTION", "COMMISSION", "FILE", "OTHER"}
    if process_type not in allowed or not title.strip() or not next_action.strip():
        raise ValidationError("نوع فرایند، عنوان و اقدام بعدی معتبر الزامی است.")
    workflow = WorkflowInstance.objects.create(space=space, process_type=process_type,
        title=title.strip(), next_action=next_action.strip(), due_date=_date(due_date), created_by=actor)
    OperationalHistory.objects.create(entity_type="WorkflowInstance", entity_id=str(workflow.pk),
        action="CREATED", previous_state=None, new_state={"state": workflow.state,
        "next_action": workflow.next_action}, responsible=actor)
    AuditEvent.objects.create(actor=actor, action="WORKFLOW_CREATE", entity_type="WorkflowInstance",
        entity_id=str(workflow.pk), after={"space": space.code, "process_type": process_type},
        ip_address=ip_address)
    return workflow


@retry_locked
@transaction.atomic
def transition_commission(*, decision: CommissionDecision, actor, new_state: str,
                          subsequent_action: str, reason: str, ip_address=None) -> CommissionDecision:
    if new_state not in CommissionDecision.State.values or not reason.strip():
        raise ValidationError("وضعیت و علت تغییر الزامی است.")
    before = {"state": decision.state, "subsequent_action": decision.subsequent_action}
    decision.state = new_state
    decision.subsequent_action = subsequent_action.strip()
    decision.save(update_fields=["state", "subsequent_action"])
    after = {"state": decision.state, "subsequent_action": decision.subsequent_action}
    OperationalHistory.objects.create(entity_type="CommissionDecision", entity_id=str(decision.pk),
        action="TRANSITION", previous_state=before, new_state=after, reason=reason.strip(), responsible=actor)
    AuditEvent.objects.create(actor=actor, action="COMMISSION_TRANSITION", entity_type="CommissionDecision",
        entity_id=str(decision.pk), reason=reason.strip(), before=before, after=after, ip_address=ip_address)
    return decision


@retry_locked
@transaction.atomic
def resolve_alert(*, alert: Alert, actor, reason: str, ip_address=None) -> Alert:
    if not reason.strip():
        raise ValidationError("شرح اقدام انجام‌شده الزامی است.")
    before = {"status": alert.status}
    alert.status = "RESOLVED"
    alert.save(update_fields=["status"])
    OperationalHistory.objects.create(entity_type="Alert", entity_id=str(alert.pk), action="RESOLVED",
        previous_state=before, new_state={"status": alert.status}, reason=reason.strip(), responsible=actor)
    AuditEvent.objects.create(actor=actor, action="ALERT_RESOLVE", entity_type="Alert",
        entity_id=str(alert.pk), reason=reason.strip(), before=before, after={"status": alert.status},
        ip_address=ip_address)
    return alert


@retry_locked
@transaction.atomic
def create_commission_decision(*, identity: str, decision_date: str, subject: str,
                               decision_text: str, spaces, actor, participants: str = "",
                               subsequent_action: str = "", document: Document | None = None,
                               ip_address=None) -> CommissionDecision:
    """Create an operational commission decision and retain its complete audit context."""
    identity, subject, decision_text = identity.strip(), subject.strip(), decision_text.strip()
    spaces = list(spaces)
    if not identity or not subject or not decision_text or not spaces:
        raise ValidationError("شناسه، موضوع، متن تصمیم و حداقل یک کد فضا الزامی است.")
    if CommissionDecision.objects.filter(identity=identity).exists():
        raise ValidationError("شناسه تصمیم کمیسیون تکراری است.")
    record = CommissionDecision.objects.create(
        identity=identity, decision_date=_date(decision_date, required=True), subject=subject,
        decision=decision_text, participants=participants.strip(),
        subsequent_action=subsequent_action.strip(), document=document,
    )
    record.spaces.set(spaces)
    codes = [space.code for space in spaces]
    AuditEvent.objects.create(
        actor=actor, action="COMMISSION_CREATE", entity_type="CommissionDecision",
        entity_id=str(record.pk), after={"identity": identity, "spaces": codes}, ip_address=ip_address,
    )
    OperationalHistory.objects.create(
        entity_type="CommissionDecision", entity_id=str(record.pk), action="CREATED",
        previous_state=None, new_state={"state": record.state, "spaces": codes}, responsible=actor,
    )
    return record


@retry_locked
@transaction.atomic
def create_appraisal(*, space, actor, values, document=None, ip_address=None):
    appraiser=values.get('appraiser','').strip()
    if not appraiser:raise ValidationError('نام کارشناس الزامی است.')
    date=_date(values.get('appraisal_date',''),required=True)
    appraisal=Appraisal.objects.create(space=space,year=date[:4],sequence=values.get('sequence','').strip(),amount_rial=_money(values.get('amount_rial',''),'مبلغ کارشناسی'),appraiser=appraiser,reference=values.get('reference','').strip(),appraisal_date=date,status=values.get('status','').strip(),created_by=actor)
    AuditEvent.objects.create(actor=actor,action='APPRAISAL_CREATE',entity_type='Appraisal',entity_id=str(appraisal.pk),after={'space':space.code,'amount_rial':str(appraisal.amount_rial)},ip_address=ip_address)
    TimelineEvent.objects.create(space=space,event_type='APPRAISAL_CREATE',jalali_date=date,source_entity='Appraisal',source_entity_id=str(appraisal.pk),title='ثبت کارشناسی جدید',description=appraisal.reference,responsible_person=actor.get_full_name() or actor.username,document=document,provenance='عملیات پس از شروع بهره‌برداری',target_url=f'/spaces/{space.code}/')
    return appraisal


@retry_locked
@transaction.atomic
def create_alert(*,space,actor,subject,reason,due_date='',target_url='',ip_address=None):
    if not subject.strip() or not reason.strip():raise ValidationError('موضوع و علت هشدار الزامی است.')
    alert=Alert.objects.create(space=space,subject=subject.strip(),reason=reason.strip(),due_date=_date(due_date),status='OPEN',target_url=target_url or f'/spaces/{space.code}/')
    AuditEvent.objects.create(actor=actor,action='ALERT_CREATE',entity_type='Alert',entity_id=str(alert.pk),after={'space':space.code,'due_date':alert.due_date},ip_address=ip_address)
    return alert
