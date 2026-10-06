from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from domains.commission.models import (
    CommissionCase,
    CommissionDecision,
    CommissionFollowUp,
    CommissionRelatedEntity,
    CommissionSession,
    CommissionSessionMember,
)
from domains.identity.models import AuditEvent
from domains.operations.models import TimelineEvent
from services.dates import normalize_jalali


def _date(value, required=False):
    value = (value or '').strip()
    if not value:
        if required:
            raise ValidationError('تاریخ الزامی است.')
        return ''
    try:
        return normalize_jalali(value)
    except ValueError as exc:
        raise ValidationError('تاریخ شمسی معتبر نیست.') from exc


def _audit(actor, action, obj, after=None, reason='', ip_address=None):
    AuditEvent.objects.create(
        actor=actor,
        action=action,
        entity_type=type(obj).__name__,
        entity_id=str(obj.pk),
        reason=reason,
        after=after or {},
        ip_address=ip_address,
    )


@transaction.atomic
def create_session(*, actor, values, members=(), ip_address=None):
    title = (values.get('title') or '').strip()
    if not title:
        raise ValidationError('عنوان جلسه الزامی است.')
    session = CommissionSession.objects.create(
        session_number=(values.get('session_number') or '').strip(),
        session_date=_date(values.get('session_date'), required=True),
        session_time=(values.get('session_time') or '').strip(),
        location=(values.get('location') or '').strip(),
        title=title,
        description=(values.get('description') or '').strip(),
        state=values.get('state') if values.get('state') in CommissionSession.State.values else CommissionSession.State.DRAFT,
        created_by=actor,
    )
    for member in members:
        CommissionSessionMember.objects.create(
            session=session,
            member=member,
            full_name=member.full_name,
            position=member.position,
            role=member.get_role_display(),
            signature_order=member.signature_order,
        )
    _audit(actor, 'COMMISSION_SESSION_CREATE', session, {'internal_code': session.internal_code, 'title': session.title}, ip_address=ip_address)
    return session


@transaction.atomic
def add_case(*, session, actor, values, related_space=None, related_contract=None, related_beneficiary=None, related_auction_period=None, related_mother_property=None, ip_address=None):
    if session.state in {CommissionSession.State.FINALIZED, CommissionSession.State.CANCELLED}:
        raise ValidationError('به جلسه نهایی یا لغوشده نمی‌توان موضوع جدید افزود.')
    title = (values.get('title') or '').strip()
    referral_reason = (values.get('referral_reason') or '').strip()
    case_type = (values.get('case_type') or '').strip()
    if not title or not referral_reason or not case_type:
        raise ValidationError('عنوان، نوع موضوع و علت ارجاع الزامی است.')
    case = CommissionCase.objects.create(
        session=session,
        title=title,
        description=(values.get('description') or '').strip(),
        referral_reason=referral_reason,
        case_type=case_type,
        referral_source=(values.get('referral_source') or '').strip(),
        follow_up_owner=(values.get('follow_up_owner') or '').strip(),
        follow_up_deadline=_date(values.get('follow_up_deadline')),
        execution_state=CommissionCase.ExecutionState.PENDING if values.get('follow_up_owner') else CommissionCase.ExecutionState.NOT_REQUIRED,
        notes=(values.get('notes') or '').strip(),
        created_by=actor,
    )
    targets = [related_space, related_contract, related_beneficiary, related_auction_period, related_mother_property]
    if not any(targets):
        raise ValidationError('حداقل یک موجودیت مرتبط باید به موضوع کمیسیون متصل شود.')
    if related_space:
        CommissionRelatedEntity.objects.create(case=case, space=related_space)
    if related_contract:
        CommissionRelatedEntity.objects.create(case=case, contract=related_contract)
    if related_beneficiary:
        CommissionRelatedEntity.objects.create(case=case, beneficiary=related_beneficiary)
    if related_auction_period:
        CommissionRelatedEntity.objects.create(case=case, auction_period=related_auction_period)
    if related_mother_property:
        CommissionRelatedEntity.objects.create(case=case, mother_property=related_mother_property)
    _audit(actor, 'COMMISSION_CASE_CREATE', case, {'internal_code': case.internal_code, 'session': session.internal_code}, ip_address=ip_address)
    return case


@transaction.atomic
def add_decision(*, case, actor, values, document=None, ip_address=None):
    formal_text = (values.get('formal_text') or '').strip()
    decision_type = (values.get('decision_type') or '').strip()
    if not formal_text or not decision_type:
        raise ValidationError('نوع مصوبه و متن رسمی مصوبه الزامی است.')
    decision = CommissionDecision.objects.create(
        case=case,
        decision_date=_date(values.get('decision_date'), required=True),
        decision_type=decision_type,
        formal_text=formal_text,
        result=(values.get('result') or '').strip(),
        execution_owner=(values.get('execution_owner') or '').strip(),
        execution_deadline=_date(values.get('execution_deadline')),
        execution_state=CommissionDecision.ExecutionState.PENDING,
        notes=(values.get('notes') or '').strip(),
        document=document,
        created_by=actor,
    )
    case.review_state = CommissionCase.ReviewState.REVIEWED
    case.result_summary = decision.result or formal_text[:255]
    if decision.execution_owner:
        case.execution_state = CommissionCase.ExecutionState.PENDING
        case.follow_up_owner = decision.execution_owner
        case.follow_up_deadline = decision.execution_deadline
    case.save(update_fields=['review_state', 'result_summary', 'execution_state', 'follow_up_owner', 'follow_up_deadline'])
    for link in case.related_entities.select_related('space'):
        if link.space_id:
            TimelineEvent.objects.create(
                space=link.space,
                event_type='COMMISSION_DECISION',
                jalali_date=decision.decision_date,
                source_entity='CommissionDecision',
                source_entity_id=str(decision.pk),
                title=f'مصوبه کمیسیون: {case.title}',
                description=decision.formal_text,
                new_state=decision.get_execution_state_display(),
                responsible_person=decision.execution_owner,
                document=document,
                provenance='اصل مصوبه در ماژول تخصصی کمیسیون معاملات',
                target_url=f'/commissions/cases/{case.pk}/',
            )
    _audit(actor, 'COMMISSION_DECISION_CREATE', decision, {'internal_code': decision.internal_code, 'case': case.internal_code}, ip_address=ip_address)
    return decision


@transaction.atomic
def add_follow_up(*, decision, actor, values, ip_address=None):
    action = (values.get('action') or '').strip()
    owner = (values.get('owner') or '').strip()
    if not action or not owner:
        raise ValidationError('اقدام پیگیری و مسئول پیگیری الزامی است.')
    follow_up = CommissionFollowUp.objects.create(
        decision=decision,
        action=action,
        owner=owner,
        due_date=_date(values.get('due_date')),
        state=CommissionFollowUp.State.OPEN,
        created_by=actor,
    )
    decision.execution_state = CommissionDecision.ExecutionState.IN_PROGRESS
    decision.save(update_fields=['execution_state'])
    case = decision.case
    case.execution_state = CommissionCase.ExecutionState.IN_PROGRESS
    case.save(update_fields=['execution_state'])
    _audit(actor, 'COMMISSION_FOLLOWUP_CREATE', follow_up, {'decision': decision.internal_code, 'owner': owner}, ip_address=ip_address)
    return follow_up


@transaction.atomic
def complete_follow_up(*, follow_up, actor, outcome, ip_address=None):
    outcome = (outcome or '').strip()
    if not outcome:
        raise ValidationError('نتیجه اقدام برای بستن پیگیری الزامی است.')
    follow_up.state = CommissionFollowUp.State.DONE
    follow_up.outcome = outcome
    follow_up.completed_at = timezone.now()
    follow_up.save(update_fields=['state', 'outcome', 'completed_at'])
    decision = follow_up.decision
    if not decision.follow_ups.exclude(state=CommissionFollowUp.State.DONE).exists():
        decision.execution_state = CommissionDecision.ExecutionState.DONE
        decision.save(update_fields=['execution_state'])
        case = decision.case
        if not case.decisions.exclude(execution_state=CommissionDecision.ExecutionState.DONE).exists():
            case.execution_state = CommissionCase.ExecutionState.DONE
            case.save(update_fields=['execution_state'])
    _audit(actor, 'COMMISSION_FOLLOWUP_COMPLETE', follow_up, {'outcome': outcome}, ip_address=ip_address)
    return follow_up
