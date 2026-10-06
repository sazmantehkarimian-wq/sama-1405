import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from domains.commission.models import CommissionDecision, CommissionMember, CommissionSession
from domains.operations.models import TimelineEvent
from domains.properties.models import CommercialSpace
from services.commission import add_case, add_decision, add_follow_up, complete_follow_up, create_session


@pytest.mark.django_db
def test_commission_session_snapshots_members_and_generates_immutable_code():
    user = get_user_model().objects.create_user(username='commission-user', password='StrongPass123!')
    member = CommissionMember.objects.create(full_name='عضو آزمایشی', position='مدیر', role='CHAIR')
    session = create_session(actor=user, values={'title': 'جلسه آزمون', 'session_date': '۱۴۰۵/۰۷/۱۴'}, members=[member])
    assert session.internal_code.startswith('COM-SES-')
    snapshot = session.session_members.get()
    assert snapshot.full_name == 'عضو آزمایشی'
    member.full_name = 'نام جدید'
    member.save(update_fields=['full_name'])
    snapshot.refresh_from_db()
    assert snapshot.full_name == 'عضو آزمایشی'
    session.internal_code = 'CHANGED'
    with pytest.raises(ValidationError):
        session.save()


@pytest.mark.django_db
def test_commission_decision_is_reflected_in_space_timeline_and_followup_closes():
    user = get_user_model().objects.create_user(username='commission-owner', password='StrongPass123!')
    space = CommercialSpace.objects.create(
        code='37', name='فضای ۳۷', status='ACTIVE', source_row=1, source_classification='TEST'
    )
    session = create_session(actor=user, values={'title': 'جلسه معاملات', 'session_date': '1405/07/14'})
    case = add_case(
        session=session,
        actor=user,
        values={'title': 'بررسی فضای ۳۷', 'case_type': 'بهره‌برداری', 'referral_reason': 'بررسی در کمیسیون'},
        related_space=space,
    )
    decision = add_decision(
        case=case,
        actor=user,
        values={
            'decision_date': '۱۴۰۵/۰۷/۱۴',
            'decision_type': 'تصویب',
            'formal_text': 'متن رسمی مصوبه آزمون',
            'execution_owner': 'اداره املاک',
            'execution_deadline': '۱۴۰۵/۰۷/۳۰',
        },
    )
    assert decision.internal_code.startswith('COM-DEC-')
    event = TimelineEvent.objects.get(space=space, source_entity='CommissionDecision', source_entity_id=str(decision.pk))
    assert event.target_url.endswith(f'/commissions/cases/{case.pk}/')
    follow_up = add_follow_up(
        decision=decision,
        actor=user,
        values={'action': 'اجرای مصوبه', 'owner': 'اداره املاک', 'due_date': '1405/07/30'},
    )
    complete_follow_up(follow_up=follow_up, actor=user, outcome='انجام شد')
    decision.refresh_from_db()
    assert decision.execution_state == CommissionDecision.ExecutionState.DONE


@pytest.mark.django_db
def test_finalized_session_rejects_new_case():
    user = get_user_model().objects.create_user(username='commission-locked', password='StrongPass123!')
    session = create_session(actor=user, values={'title': 'جلسه نهایی', 'session_date': '1405/07/14'})
    session.state = CommissionSession.State.FINALIZED
    session.save(update_fields=['state'])
    space = CommercialSpace.objects.create(code='38', name='فضای ۳۸', status='ACTIVE', source_row=2, source_classification='TEST')
    with pytest.raises(ValidationError):
        add_case(
            session=session,
            actor=user,
            values={'title': 'موضوع ممنوع', 'case_type': 'آزمون', 'referral_reason': 'آزمون'},
            related_space=space,
        )
