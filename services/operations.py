"""Transactional operational commands shared by UI and future API callers."""
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from domains.identity.models import AuditEvent
from domains.documents.models import Document
from domains.operations.models import (
    Alert, Appraisal, AppraisalFee, AppraisalNotification, CommissionDecision,
    ExpertFeeBatchItem, ExpertFeePaymentBatch, OperationalHistory,
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


def _timeline(*, space, actor, event_type, source, source_id, title, date="", description="", previous="", new="", document=None):
    TimelineEvent.objects.create(space=space,event_type=event_type,jalali_date=date,occurred_at=timezone.now(),source_entity=source,source_entity_id=str(source_id),title=title,description=description,previous_state=previous,new_state=new,responsible_person=actor.get_full_name() or actor.username,document=document,provenance="رویداد عملیاتی ثبت‌شده در سامانه",target_url=f"/spaces/{space.code}/")


@retry_locked
@transaction.atomic
def create_appraisal_fee(*, appraisal: Appraisal, actor, amount, notes="", document: Document | None = None,
                         follow_up_date="", ip_address=None) -> AppraisalFee:
    if hasattr(appraisal, "fee"):
        raise ValidationError("برای این کارشناسی قبلاً پرونده حق‌الزحمه ثبت شده است.")
    if not appraisal.appraiser_ref_id:
        raise ValidationError("کارشناسی بدون کارشناس ثبت‌شده نمی‌تواند پرونده حق‌الزحمه داشته باشد.")
    fee = AppraisalFee.objects.create(
        appraisal=appraisal,
        amount_rial=_money(amount, "حق‌الزحمه"),
        status=AppraisalFee.Status.FEE_ENTERED,
        follow_up_date=_date(follow_up_date),
        notes=(notes or "").strip(),
        supporting_document=document,
        created_by=actor,
    )
    AuditEvent.objects.create(
        actor=actor, action="APPRAISAL_FEE_CREATE", entity_type="AppraisalFee",
        entity_id=str(fee.pk),
        after={"code":fee.sama_code,"space":appraisal.space.code,"appraiser_id":appraisal.appraiser_ref_id,
               "amount_rial":str(fee.amount_rial),"status":fee.status},
        ip_address=ip_address,
    )
    OperationalHistory.objects.create(
        entity_type="AppraisalFee",entity_id=str(fee.pk),action="CREATED",
        previous_state=None,new_state={"amount_rial":str(fee.amount_rial),"status":fee.status},responsible=actor,
    )
    _timeline(
        space=appraisal.space,actor=actor,event_type="APPRAISAL_FEE_CREATE",source="AppraisalFee",source_id=fee.pk,
        title=f"ثبت حق‌الزحمه {fee.sama_code}",date=fee.follow_up_date,new=fee.status,document=document,
    )
    return fee


def record_appraisal_fee(*, appraisal: Appraisal, actor, amount: str, payment_status: str = "",
                         payment_date: str = "", payment_reference: str = "",
                         follow_up_date: str = "", notes: str = "", document: Document | None = None,
                         ip_address=None) -> AppraisalFee:
    """Compatibility entry point; new records always start at FEE_ENTERED unless a valid full payment is requested."""
    fee=create_appraisal_fee(
        appraisal=appraisal,actor=actor,amount=amount,notes=notes,document=document,
        follow_up_date=follow_up_date,ip_address=ip_address,
    )
    return fee


@retry_locked
@transaction.atomic
def update_appraisal_fee_amount(*,fee:AppraisalFee,actor,amount,reason,ip_address=None):
    reason=(reason or "").strip()
    if not reason:raise ValidationError("علت اصلاح مبلغ الزامی است.")
    if fee.status in {AppraisalFee.Status.PAID,AppraisalFee.Status.CLOSED}:
        raise ValidationError("پس از پرداخت یا مختومه‌شدن، اصلاح مستقیم مبلغ مجاز نیست.")
    new_amount=_money(amount,"حق‌الزحمه")
    before=str(fee.amount_rial)
    fee.amount_rial=new_amount
    fee.save(update_fields=["amount_rial","updated_at"])
    AuditEvent.objects.create(
        actor=actor,action="APPRAISAL_FEE_AMOUNT_UPDATE",entity_type="AppraisalFee",entity_id=str(fee.pk),
        reason=reason,before={"amount_rial":before},after={"amount_rial":str(new_amount)},ip_address=ip_address,
    )
    OperationalHistory.objects.create(
        entity_type="AppraisalFee",entity_id=str(fee.pk),action="AMOUNT_UPDATED",
        previous_state={"amount_rial":before},new_state={"amount_rial":str(new_amount)},reason=reason,responsible=actor,
    )
    return fee


_ALLOWED_FEE_TRANSITIONS={
    AppraisalFee.Status.FEE_ENTERED:{AppraisalFee.Status.READY_TO_SEND,AppraisalFee.Status.NEEDS_CORRECTION,AppraisalFee.Status.STOPPED,AppraisalFee.Status.CANCELLED},
    AppraisalFee.Status.READY_TO_SEND:{AppraisalFee.Status.SENT_TO_FINANCE,AppraisalFee.Status.NEEDS_CORRECTION,AppraisalFee.Status.STOPPED,AppraisalFee.Status.CANCELLED},
    AppraisalFee.Status.SENT_TO_FINANCE:{AppraisalFee.Status.IN_PROGRESS,AppraisalFee.Status.PAID,AppraisalFee.Status.NEEDS_CORRECTION,AppraisalFee.Status.STOPPED},
    AppraisalFee.Status.IN_PROGRESS:{AppraisalFee.Status.PAID,AppraisalFee.Status.NEEDS_CORRECTION,AppraisalFee.Status.STOPPED},
    AppraisalFee.Status.NEEDS_CORRECTION:{AppraisalFee.Status.FEE_ENTERED,AppraisalFee.Status.READY_TO_SEND,AppraisalFee.Status.CANCELLED},
    AppraisalFee.Status.STOPPED:{AppraisalFee.Status.READY_TO_SEND,AppraisalFee.Status.CANCELLED},
    AppraisalFee.Status.PAID:{AppraisalFee.Status.CLOSED},
    AppraisalFee.Status.CLOSED:set(),
    AppraisalFee.Status.CANCELLED:set(),
}


@retry_locked
@transaction.atomic
def transition_appraisal_fee(*,fee:AppraisalFee,actor,new_status,values=None,reason="",ip_address=None):
    values=values or {}
    if new_status not in AppraisalFee.Status.values:raise ValidationError("وضعیت حق‌الزحمه معتبر نیست.")
    if new_status not in _ALLOWED_FEE_TRANSITIONS.get(fee.status,set()):
        raise ValidationError("این تغییر وضعیت در گردش حق‌الزحمه مجاز نیست.")
    reason=(reason or values.get("reason") or "").strip()
    before={
        "status":fee.status,"sent_to_finance_date":fee.sent_to_finance_date,"letter_number":fee.letter_number,
        "letter_date":fee.letter_date,"payment_date":fee.payment_date,
        "paid_amount_rial":str(fee.paid_amount_rial) if fee.paid_amount_rial is not None else None,
        "payment_reference":fee.payment_reference,
    }
    if new_status==AppraisalFee.Status.SENT_TO_FINANCE:
        sent=_date(values.get("sent_to_finance_date"),required=True)
        letter=(values.get("letter_number") or "").strip()
        letter_date=_date(values.get("letter_date"),required=True)
        if not letter:raise ValidationError("شماره نامه / گردش برای ارسال به مالی الزامی است.")
        fee.sent_to_finance_date=sent;fee.letter_number=letter;fee.letter_date=letter_date
    if new_status==AppraisalFee.Status.PAID:
        payment_date=_date(values.get("payment_date"),required=True)
        paid=_money(values.get("paid_amount_rial"),"مبلغ پرداخت‌شده")
        reference=(values.get("payment_reference") or "").strip()
        if not reference:raise ValidationError("مرجع پرداخت الزامی است.")
        if paid!=fee.amount_rial:
            raise ValidationError("مبلغ پرداخت‌شده باید دقیقاً با مبلغ حق‌الزحمه برابر باشد.")
        fee.payment_date=payment_date;fee.paid_amount_rial=paid;fee.payment_reference=reference
    if new_status in {AppraisalFee.Status.NEEDS_CORRECTION,AppraisalFee.Status.STOPPED,AppraisalFee.Status.CANCELLED} and not reason:
        raise ValidationError("علت تغییر وضعیت الزامی است.")
    previous=fee.status
    fee.status=new_status
    fee.save(update_fields=[
        "status","sent_to_finance_date","letter_number","letter_date","payment_date",
        "paid_amount_rial","payment_reference","updated_at",
    ])
    AuditEvent.objects.create(
        actor=actor,action="APPRAISAL_FEE_TRANSITION",entity_type="AppraisalFee",entity_id=str(fee.pk),
        reason=reason,before=before,after={
            "status":fee.status,"sent_to_finance_date":fee.sent_to_finance_date,"letter_number":fee.letter_number,
            "letter_date":fee.letter_date,"payment_date":fee.payment_date,
            "paid_amount_rial":str(fee.paid_amount_rial) if fee.paid_amount_rial is not None else None,
            "payment_reference":fee.payment_reference,
        },ip_address=ip_address,
    )
    OperationalHistory.objects.create(
        entity_type="AppraisalFee",entity_id=str(fee.pk),action="TRANSITION",
        previous_state={"status":previous},new_state={"status":fee.status},reason=reason,responsible=actor,
    )
    _timeline(
        space=fee.appraisal.space,actor=actor,event_type="APPRAISAL_FEE_TRANSITION",source="AppraisalFee",source_id=fee.pk,
        title=f"تغییر وضعیت حق‌الزحمه {fee.sama_code}",date=fee.payment_date or fee.sent_to_finance_date,
        previous=previous,new=fee.status,description=reason,
    )
    return fee


@retry_locked
@transaction.atomic
def create_fee_payment_batch(*,fees,actor,sent_date,letter_number,letter_date,notes="",ip_address=None):
    fee_ids=[fee.pk for fee in fees]
    locked=list(AppraisalFee.objects.select_for_update().filter(pk__in=fee_ids).select_related("appraisal__space","appraisal__appraiser_ref"))
    if not locked:raise ValidationError("حداقل یک حق‌الزحمه باید انتخاب شود.")
    if len(locked)!=len(set(fee_ids)):raise ValidationError("یک یا چند رکورد حق‌الزحمه معتبر نیست.")
    if any(fee.status!=AppraisalFee.Status.READY_TO_SEND for fee in locked):
        raise ValidationError("فقط رکوردهای «آماده ارسال» می‌توانند وارد Batch شوند.")
    if ExpertFeeBatchItem.objects.filter(fee__in=locked,active=True).exists():
        raise ValidationError("حداقل یک رکورد در Batch فعال دیگری عضو است.")
    sent=_date(sent_date,required=True);letter_date_value=_date(letter_date,required=True)
    letter=(letter_number or "").strip()
    if not letter:raise ValidationError("شماره نامه / گردش Batch الزامی است.")
    batch=ExpertFeePaymentBatch.objects.create(
        sent_date=sent,letter_number=letter,letter_date=letter_date_value,
        status=ExpertFeePaymentBatch.Status.SENT,notes=(notes or "").strip(),created_by=actor,
    )
    year=sent[:4]
    batch.code=f"PAY-{year}-{batch.pk:03d}"
    batch.save(update_fields=["code","updated_at"])
    for fee in locked:
        ExpertFeeBatchItem.objects.create(batch=batch,fee=fee,active=True,added_by=actor)
        transition_appraisal_fee(
            fee=fee,actor=actor,new_status=AppraisalFee.Status.SENT_TO_FINANCE,
            values={"sent_to_finance_date":sent,"letter_number":letter,"letter_date":letter_date_value},
            reason=f"ارسال گروهی در {batch.code}",ip_address=ip_address,
        )
    AuditEvent.objects.create(
        actor=actor,action="APPRAISAL_FEE_BATCH_CREATE",entity_type="ExpertFeePaymentBatch",entity_id=str(batch.pk),
        after={"code":batch.code,"fee_ids":[fee.pk for fee in locked],"count":len(locked),"letter_number":letter},
        ip_address=ip_address,
    )
    return batch


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
    _timeline(space=space,actor=actor,event_type="UTILITY_RECORD_CREATE",source="UtilityRecord",source_id=record.pk,title="ثبت صورتحساب انشعاب",date=record.period_end,new=record.payment_status,description=record.get_utility_type_display(),document=document)
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
    _timeline(space=workflow.space,actor=actor,event_type="WORKFLOW_TRANSITION",source="WorkflowInstance",source_id=workflow.pk,title=f"تغییر وضعیت فرایند {workflow.title}",date=workflow.due_date,previous=before["state"],new=workflow.state,description=workflow.next_action)
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
    _timeline(space=space,actor=actor,event_type="WORKFLOW_CREATE",source="WorkflowInstance",source_id=workflow.pk,title=f"ایجاد فرایند {workflow.title}",date=workflow.due_date,new=workflow.state,description=workflow.next_action)
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
    for space in decision.spaces.all():_timeline(space=space,actor=actor,event_type="COMMISSION_TRANSITION",source="CommissionDecision",source_id=decision.pk,title=f"تغییر وضعیت تصمیم کمیسیون {decision.identity}",date=decision.decision_date,previous=before["state"],new=decision.state,description=reason)
    return decision


@retry_locked
@transaction.atomic
def resolve_alert(*, alert: Alert, actor, reason: str, ip_address=None) -> Alert:
    if not reason.strip():
        raise ValidationError("شرح اقدام انجام‌شده الزامی است.")
    before = {"status": alert.status}
    alert.status = "RESOLVED"
    alert.assigned_to = alert.assigned_to or actor
    alert.acknowledged_at = alert.acknowledged_at or timezone.now()
    alert.save(update_fields=["status","assigned_to","acknowledged_at"])
    OperationalHistory.objects.create(entity_type="Alert", entity_id=str(alert.pk), action="RESOLVED",
        previous_state=before, new_state={"status": alert.status}, reason=reason.strip(), responsible=actor)
    AuditEvent.objects.create(actor=actor, action="ALERT_RESOLVE", entity_type="Alert",
        entity_id=str(alert.pk), reason=reason.strip(), before=before, after={"status": alert.status},
        ip_address=ip_address)
    _timeline(space=alert.space,actor=actor,event_type="ALERT_RESOLVE",source="Alert",source_id=alert.pk,title=f"مختومه‌سازی مورد پیگیری: {alert.subject}",previous=before["status"],new=alert.status,description=reason)
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
    for space in spaces:_timeline(space=space,actor=actor,event_type="COMMISSION_CREATE",source="CommissionDecision",source_id=record.pk,title=f"ثبت تصمیم کمیسیون {identity}",date=record.decision_date,new=record.state,description=record.subject,document=document)
    return record


@retry_locked
@transaction.atomic
def create_appraisal(*, space, appraiser, actor, values, document=None, ip_address=None):
    if appraiser is None:
        raise ValidationError("انتخاب کارشناس ثبت‌شده الزامی است.")

    appraisal_date = _date(values.get("appraisal_date", ""))
    response_date = _date(values.get("response_date", ""))
    amount_value = values.get("amount_rial", "")
    amount = _money(amount_value, "مبلغ کارشناسی") if amount_value not in (None, "") else None

    is_current = values.get("is_current") in (True, "on", "1")
    if is_current and (not appraisal_date or amount is None):
        raise ValidationError("کارشناسی مرجع باید تاریخ خود کارشناسی و مبلغ کارشناسی داشته باشد.")
    if is_current:
        Appraisal.objects.filter(space=space, is_current=True).update(is_current=False)

    appraisal = Appraisal.objects.create(
        space=space,
        appraiser=appraiser.full_name,
        appraiser_ref=appraiser,
        year=appraisal_date[:4] if appraisal_date else "",
        sequence=str(values.get("sequence", "") or "").strip(),
        amount_rial=amount,
        reference=str(values.get("reference", "") or "").strip(),
        response_number=str(values.get("response_number", "") or "").strip(),
        response_date=response_date,
        appraisal_date=appraisal_date,
        status=str(values.get("status", "") or "").strip(),
        is_current=is_current,
        notes=str(values.get("notes", "") or "").strip(),
        created_by=actor,
    )

    notification_date = _date(values.get("notification_date", ""))
    notification_recipient = values.get("notification_recipient", "")
    notification_number = str(values.get("notification_number", "") or "").strip()
    if any((notification_date, notification_recipient, notification_number)):
        if not notification_date or notification_recipient not in AppraisalNotification.Recipient.values:
            raise ValidationError("برای ثبت ابلاغ، تاریخ و مخاطب معتبر الزامی است.")
        AppraisalNotification.objects.create(
            appraisal=appraisal,
            number=notification_number,
            notification_date=notification_date,
            recipient=notification_recipient,
            recipient_detail=str(values.get("notification_recipient_detail", "") or "").strip(),
            notes=str(values.get("notification_notes", "") or "").strip(),
            document=document,
            created_by=actor,
        )

    AuditEvent.objects.create(
        actor=actor,
        action="APPRAISAL_CREATE",
        entity_type="Appraisal",
        entity_id=str(appraisal.pk),
        after={
            "space": space.code,
            "appraisal_code": appraisal.sama_code,
            "appraiser_id": appraiser.pk,
            "appraisal_date": appraisal.appraisal_date,
            "amount_rial": str(appraisal.amount_rial) if appraisal.amount_rial is not None else None,
            "is_current": appraisal.is_current,
        },
        ip_address=ip_address,
    )
    TimelineEvent.objects.create(
        space=space,
        event_type="APPRAISAL_CREATE",
        jalali_date=appraisal.appraisal_date or response_date or notification_date,
        source_entity="Appraisal",
        source_entity_id=str(appraisal.pk),
        title=f"ثبت کارشناسی {appraisal.sama_code}",
        description=f"کارشناس: {appraiser.full_name}",
        responsible_person=actor.get_full_name() or actor.username,
        document=document,
        provenance="ثبت دستی کنترل‌شده در سما",
        target_url=f"/spaces/{space.code}/",
    )
    return appraisal


@retry_locked
@transaction.atomic
def create_alert(*,space,actor,subject,reason,due_date='',priority='MEDIUM',target_url='',ip_address=None):
    if not subject.strip() or not reason.strip():raise ValidationError('موضوع و علت هشدار الزامی است.')
    if priority not in Alert.Priority.values:raise ValidationError('اولویت مورد پیگیری معتبر نیست.')
    alert=Alert.objects.create(space=space,subject=subject.strip(),reason=reason.strip(),due_date=_date(due_date),priority=priority,status='OPEN',assigned_to=actor,target_url=target_url or f'/spaces/{space.code}/')
    AuditEvent.objects.create(actor=actor,action='ALERT_CREATE',entity_type='Alert',entity_id=str(alert.pk),after={'space':space.code,'due_date':alert.due_date},ip_address=ip_address)
    _timeline(space=space,actor=actor,event_type='ALERT_CREATE',source='Alert',source_id=alert.pk,title=f'ثبت مورد نیازمند پیگیری: {alert.subject}',date=alert.due_date,new=alert.status,description=alert.reason)
    return alert
