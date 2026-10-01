import pytest
from django.contrib.auth import get_user_model

from domains.contracts.models import Beneficiary, Contract
from domains.identity.models import AuditEvent
from domains.operations.models import (
    CommissionCase, CommissionDecision, CommissionFollowUp, CommissionFollowUpHistory,
    CommissionMember, CommissionSession, CommissionSessionMember, TimelineEvent,
)
from domains.properties.models import CommercialSpace


@pytest.mark.django_db
def test_commission_session_snapshots_members_and_keeps_history(client):
    user=get_user_model().objects.create_user("commission-owner",password="A-very-safe-password",is_staff=True)
    client.force_login(user)
    member=CommissionMember.objects.create(
        name="عضو اول",position="مدیر",role="عضو",sign_order=2,status="ACTIVE",created_by=user,
    )
    response=client.post("/commissions/sessions/new/",{
        "number":"12","session_date":"1405/07/10","session_time":"09:30",
        "title":"جلسه معاملات","status":"HELD","members":[member.pk],
    })
    assert response.status_code==302
    session=CommissionSession.objects.get()
    snap=CommissionSessionMember.objects.get(session=session)
    assert snap.name=="عضو اول" and snap.position=="مدیر" and snap.sign_order==2

    member.position="سمت جدید";member.sign_order=5;member.save(update_fields=["position","sign_order","updated_at"])
    snap.refresh_from_db()
    assert snap.position=="مدیر" and snap.sign_order==2
    assert AuditEvent.objects.filter(action="COMMISSION_SESSION_CREATE",entity_id=str(session.pk)).exists()


@pytest.mark.django_db
def test_commission_case_links_are_explicit_and_decision_is_visible_on_space_timeline(client):
    user=get_user_model().objects.create_user("commission-case",password="A-very-safe-password")
    client.force_login(user)
    space=CommercialSpace.objects.create(code="8801",name="فضای کمیسیون",status="ACTIVE")
    beneficiary=Beneficiary.objects.create(kind="LEGAL",name="شرکت کمیسیون",legal_name="شرکت کمیسیون")
    contract=Contract.objects.create(
        space=space,beneficiary=beneficiary,number="COM-C",start_date="1405/01/01",end_date="1405/12/29",
    )
    session=CommissionSession.objects.create(session_date="1405/07/10",title="جلسه",created_by=user)

    response=client.post(f"/commissions/sessions/{session.pk}/cases/new/",{
        "title":"بررسی تمدید","reason":"طرح رسمی","case_type":"قرارداد",
        "spaces":[space.pk],"contracts":[contract.pk],"beneficiaries":[beneficiary.pk],
    })
    assert response.status_code==302
    case=CommissionCase.objects.get()
    assert list(case.spaces.all())==[space]
    assert list(case.contracts.all())==[contract]
    assert list(case.beneficiaries.all())==[beneficiary]

    response=client.post(f"/commissions/cases/{case.pk}/decisions/new/",{
        "decision_date":"1405/07/10","decision_type":"مصوبه",
        "decision":"تمدید منوط به بررسی حقوقی است.",
        "responsible":user.pk,"due_date":"1405/07/20","execution_status":"ACTION_REQUIRED",
        "subsequent_action":"ارجاع به حقوقی",
    })
    assert response.status_code==302
    decision=CommissionDecision.objects.get(case=case)
    assert decision.decision=="تمدید منوط به بررسی حقوقی است."
    assert decision.execution_status=="ACTION_REQUIRED"
    assert set(decision.spaces.all())=={space}
    assert TimelineEvent.objects.filter(space=space,event_type="COMMISSION_DECISION_CREATE").exists()
    assert AuditEvent.objects.filter(action="COMMISSION_DECISION_CREATE",entity_id=str(decision.pk)).exists()


@pytest.mark.django_db
def test_commission_action_decision_requires_responsible_user(client):
    user=get_user_model().objects.create_user("commission-validation",password="A-very-safe-password")
    client.force_login(user)
    session=CommissionSession.objects.create(session_date="1405/07/10",title="جلسه",created_by=user)
    case=CommissionCase.objects.create(session=session,title="موضوع",created_by=user)
    response=client.post(f"/commissions/cases/{case.pk}/decisions/new/",{
        "decision_date":"1405/07/10","decision":"اقدام شود","execution_status":"ACTION_REQUIRED",
    })
    assert response.status_code==200
    assert CommissionDecision.objects.filter(case=case).count()==0
    assert "مسئول پیگیری الزامی است" in response.content.decode()


@pytest.mark.django_db
def test_commission_followup_status_history_is_append_only(client):
    user=get_user_model().objects.create_user("commission-followup",password="A-very-safe-password")
    client.force_login(user)
    session=CommissionSession.objects.create(session_date="1405/07/10",title="جلسه",created_by=user)
    case=CommissionCase.objects.create(session=session,title="موضوع",created_by=user)
    decision=CommissionDecision.objects.create(
        identity="D-1",decision_date="1405/07/10",subject="موضوع",decision="اقدام شود",
        case=case,responsible=user,execution_status="ACTION_REQUIRED",created_by=user,
    )

    response=client.post(f"/commissions/decisions/{decision.pk}/followups/new/",{
        "required_action":"پیگیری نامه","responsible":user.pk,"responsible_unit":"حقوقی",
        "referred_date":"1405/07/11","due_date":"1405/07/20","status":"ACTION_REQUIRED",
    })
    assert response.status_code==302
    followup=CommissionFollowUp.objects.get()
    assert followup.history.count()==1

    response=client.post(f"/commissions/followups/{followup.pk}/transition/",{
        "status":"IN_PROGRESS","note":"ارجاع انجام شد",
    })
    assert response.status_code==302
    response=client.post(f"/commissions/followups/{followup.pk}/transition/",{
        "status":"DONE","completed_date":"1405/07/18","result":"نامه دریافت شد","note":"تکمیل",
    })
    assert response.status_code==302
    followup.refresh_from_db();decision.refresh_from_db()
    assert followup.status=="DONE" and decision.execution_status=="DONE"
    history=list(CommissionFollowUpHistory.objects.filter(followup=followup).order_by("changed_at","id"))
    assert [x.new_status for x in history]==["ACTION_REQUIRED","IN_PROGRESS","DONE"]
    assert AuditEvent.objects.filter(action="COMMISSION_FOLLOWUP_TRANSITION",entity_id=str(followup.pk)).count()==2
