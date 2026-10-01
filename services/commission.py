from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from domains.identity.models import AuditEvent
from domains.operations.models import (
    CommissionCase, CommissionDecision, CommissionFollowUp,
    CommissionFollowUpHistory, CommissionMember, CommissionSession,
    CommissionSessionMember, TimelineEvent,
)
from services.database import retry_locked
from services.dates import normalize_jalali


def _date(value, *, required=False):
    raw=(value or "").strip()
    if not raw and not required:
        return ""
    try:
        result=normalize_jalali(raw)
    except ValueError as exc:
        raise ValidationError("تاریخ شمسی معتبر نیست.") from exc
    if required and not result:
        raise ValidationError("تاریخ الزامی است.")
    return result


def _timeline_for_case(case, *, actor, event_type, title, description="", date="", previous="", new=""):
    for space in case.spaces.all():
        TimelineEvent.objects.create(
            space=space,event_type=event_type,jalali_date=date,
            source_entity="CommissionCase",source_entity_id=str(case.pk),
            title=title,description=description,previous_state=previous,new_state=new,
            responsible_person=actor.get_full_name() or actor.username,
            provenance="ثبت ساختاریافته در ماژول کمیسیون معاملات",
            target_url=f"/commissions/sessions/{case.session_id}/",
        )


@retry_locked
@transaction.atomic
def create_session(*, actor, values, members=None, ip_address=None):
    title=(values.get("title") or "").strip()
    date=_date(values.get("session_date"),required=True)
    if not title:
        raise ValidationError("عنوان جلسه الزامی است.")
    session=CommissionSession.objects.create(
        number=(values.get("number") or "").strip(),
        session_date=date,
        session_time=(values.get("session_time") or "").strip(),
        location=(values.get("location") or "").strip(),
        title=title,
        description=(values.get("description") or "").strip(),
        status=values.get("status") if values.get("status") in CommissionSession.Status.values else CommissionSession.Status.DRAFT,
        notes=(values.get("notes") or "").strip(),
        created_by=actor,
    )
    selected=list(members or CommissionMember.objects.filter(status=CommissionMember.Status.ACTIVE))
    for member in selected:
        CommissionSessionMember.objects.create(
            session=session,member=member,name=member.name,position=member.position,
            role=member.role,present=True,sign_order=member.sign_order,notes="",
        )
    AuditEvent.objects.create(
        actor=actor,action="COMMISSION_SESSION_CREATE",entity_type="CommissionSession",
        entity_id=str(session.pk),
        after={"code":session.sama_code,"date":session.session_date,"title":session.title,"member_count":len(selected)},
        ip_address=ip_address,
    )
    return session


@retry_locked
@transaction.atomic
def create_case(*, session, actor, values, spaces=(), contracts=(), beneficiaries=(), auction_periods=(), ip_address=None):
    title=(values.get("title") or "").strip()
    if not title:
        raise ValidationError("عنوان موضوع کمیسیون الزامی است.")
    case=CommissionCase.objects.create(
        session=session,title=title,description=(values.get("description") or "").strip(),
        reason=(values.get("reason") or "").strip(),case_type=(values.get("case_type") or "").strip(),
        referral_reference=(values.get("referral_reference") or "").strip(),
        status=CommissionCase.Status.OPEN,responsible=values.get("responsible"),
        follow_up_due_date=_date(values.get("follow_up_due_date")),notes=(values.get("notes") or "").strip(),
        created_by=actor,
    )
    case.spaces.set(list(spaces));case.contracts.set(list(contracts));case.beneficiaries.set(list(beneficiaries));case.auction_periods.set(list(auction_periods))
    AuditEvent.objects.create(
        actor=actor,action="COMMISSION_CASE_CREATE",entity_type="CommissionCase",entity_id=str(case.pk),
        after={
            "code":case.sama_code,"session":session.sama_code,
            "spaces":[x.code for x in case.spaces.all()],
            "contracts":[x.pk for x in case.contracts.all()],
            "beneficiaries":[x.pk for x in case.beneficiaries.all()],
            "auction_periods":[x.pk for x in case.auction_periods.all()],
        },ip_address=ip_address,
    )
    _timeline_for_case(case,actor=actor,event_type="COMMISSION_CASE_CREATE",title=f"طرح موضوع کمیسیون {case.sama_code}",description=case.title,date=session.session_date,new=case.status)
    return case


@retry_locked
@transaction.atomic
def create_case_decision(*, case, actor, values, document=None, ip_address=None):
    decision_text=(values.get("decision") or "").strip()
    date=_date(values.get("decision_date"),required=True)
    if not decision_text:
        raise ValidationError("متن رسمی تصمیم الزامی است.")
    responsible=values.get("responsible")
    execution_status=values.get("execution_status") or CommissionDecision.ExecutionStatus.ACTION_REQUIRED
    if execution_status not in CommissionDecision.ExecutionStatus.values:
        raise ValidationError("وضعیت اجرای تصمیم معتبر نیست.")
    if execution_status in {CommissionDecision.ExecutionStatus.ACTION_REQUIRED,CommissionDecision.ExecutionStatus.IN_PROGRESS} and responsible is None:
        raise ValidationError("برای تصمیم نیازمند اقدام، مسئول پیگیری الزامی است.")
    decision=CommissionDecision.objects.create(
        identity=(values.get("identity") or "").strip() or f"{case.sama_code}-D{case.decisions.count()+1}",
        decision_date=date,subject=case.title,decision=decision_text,
        decision_type=(values.get("decision_type") or "").strip(),
        result=(values.get("result") or "").strip(),case=case,responsible=responsible,
        due_date=_date(values.get("due_date")),execution_status=execution_status,
        subsequent_action=(values.get("subsequent_action") or "").strip(),
        state=CommissionDecision.State.APPROVED,document=document,created_by=actor,
    )
    decision.spaces.set(case.spaces.all())
    case.status=CommissionCase.Status.DECIDED
    case.save(update_fields=["status","updated_at"])
    AuditEvent.objects.create(
        actor=actor,action="COMMISSION_DECISION_CREATE",entity_type="CommissionDecision",entity_id=str(decision.pk),
        after={"code":decision.sama_code,"case":case.sama_code,"execution_status":decision.execution_status,"due_date":decision.due_date},
        ip_address=ip_address,
    )
    _timeline_for_case(case,actor=actor,event_type="COMMISSION_DECISION_CREATE",title=f"ثبت تصمیم کمیسیون {decision.sama_code}",description=decision.decision,date=date,new=execution_status)
    return decision


@retry_locked
@transaction.atomic
def create_followup(*, decision, actor, values, ip_address=None):
    action=(values.get("required_action") or "").strip()
    if not action:
        raise ValidationError("اقدام موردنیاز الزامی است.")
    status=values.get("status") or CommissionDecision.ExecutionStatus.ACTION_REQUIRED
    if status not in CommissionDecision.ExecutionStatus.values:
        raise ValidationError("وضعیت پیگیری معتبر نیست.")
    followup=CommissionFollowUp.objects.create(
        decision=decision,required_action=action,responsible=values.get("responsible"),
        responsible_unit=(values.get("responsible_unit") or "").strip(),
        referred_date=_date(values.get("referred_date")),due_date=_date(values.get("due_date")),
        status=status,completed_date=_date(values.get("completed_date")),
        result=(values.get("result") or "").strip(),notes=(values.get("notes") or "").strip(),
        created_by=actor,
    )
    CommissionFollowUpHistory.objects.create(
        followup=followup,previous_status="",new_status=status,note="ایجاد پیگیری",changed_by=actor,
    )
    AuditEvent.objects.create(
        actor=actor,action="COMMISSION_FOLLOWUP_CREATE",entity_type="CommissionFollowUp",entity_id=str(followup.pk),
        after={"decision":decision.sama_code,"status":status,"due_date":followup.due_date},ip_address=ip_address,
    )
    if decision.case_id:
        _timeline_for_case(decision.case,actor=actor,event_type="COMMISSION_FOLLOWUP_CREATE",title=f"ایجاد پیگیری {decision.sama_code}",description=action,date=followup.referred_date or decision.decision_date,new=status)
    return followup


@retry_locked
@transaction.atomic
def transition_followup(*, followup, actor, new_status, note="", completed_date="", result="", ip_address=None):
    if new_status not in CommissionDecision.ExecutionStatus.values:
        raise ValidationError("وضعیت پیگیری معتبر نیست.")
    if new_status==followup.status:
        raise ValidationError("وضعیت جدید با وضعیت فعلی یکسان است.")
    if new_status in {CommissionDecision.ExecutionStatus.DONE,CommissionDecision.ExecutionStatus.CLOSED} and not result.strip():
        raise ValidationError("برای انجام/مختومه شدن، نتیجه اقدام الزامی است.")
    before=followup.status
    followup.status=new_status
    if completed_date:
        followup.completed_date=_date(completed_date)
    if result.strip():
        followup.result=result.strip()
    followup.save(update_fields=["status","completed_date","result","updated_at"])
    CommissionFollowUpHistory.objects.create(
        followup=followup,previous_status=before,new_status=new_status,note=(note or "").strip(),changed_by=actor,
    )
    decision=followup.decision
    decision.execution_status=new_status
    decision.save(update_fields=["execution_status","updated_at"])
    AuditEvent.objects.create(
        actor=actor,action="COMMISSION_FOLLOWUP_TRANSITION",entity_type="CommissionFollowUp",entity_id=str(followup.pk),
        before={"status":before},after={"status":new_status,"completed_date":followup.completed_date},
        reason=(note or "").strip(),ip_address=ip_address,
    )
    if decision.case_id:
        _timeline_for_case(decision.case,actor=actor,event_type="COMMISSION_FOLLOWUP_TRANSITION",title=f"تغییر وضعیت پیگیری {decision.sama_code}",description=(note or "").strip(),date=followup.completed_date or decision.decision_date,previous=before,new=new_status)
    return followup
