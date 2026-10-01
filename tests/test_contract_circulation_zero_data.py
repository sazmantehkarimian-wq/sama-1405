import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from domains.contracts.models import (
    Beneficiary, Contract, ContractCirculation, ContractCustodyTransfer,
    ContractFinalApproval, ContractSignatureStep,
)
from domains.identity.models import AuditEvent
from domains.properties.models import CommercialSpace
from services.contract_circulation import (
    add_signature_step, close_without_contract, convert_to_contract, create_circulation,
    current_custody, final_approve, return_custody, transfer_custody,
    transition_signature_step,
)


@pytest.fixture
def circulation_context(db):
    user=get_user_model().objects.create_user("circulation-user",password="A-very-safe-password")
    space=CommercialSpace.objects.create(code="8301",name="فضای قرارداد",status="ACTIVE")
    beneficiary=Beneficiary.objects.create(kind="LEGAL",name="شرکت گردش",legal_name="شرکت گردش")
    return user,space,beneficiary


@pytest.mark.django_db
def test_circulation_is_not_contract_and_respects_operational_start(circulation_context):
    user,space,beneficiary=circulation_context
    with pytest.raises(ValidationError):
        create_circulation(
            space=space,beneficiary=beneficiary,subject="گردش",operational_start_date="1405/06/31",
            next_action="بررسی",actor=user,
        )
    case=create_circulation(
        space=space,beneficiary=beneficiary,subject="گردش",operational_start_date="1405/07/01",
        next_action="بررسی",actor=user,
    )
    assert case.identity.startswith("CC-")
    assert case.official_contract_id is None
    assert Contract.objects.filter(space=space).count()==0


@pytest.mark.django_db
def test_signature_roles_are_manual_and_required_steps_gate_approval(circulation_context):
    user,space,beneficiary=circulation_context
    case=create_circulation(
        space=space,beneficiary=beneficiary,subject="امضا",operational_start_date="1405/07/01",
        next_action="ثبت مراحل امضا",actor=user,
    )
    with pytest.raises(ValidationError):
        final_approve(circulation=case,actor=user)

    step=add_signature_step(
        circulation=case,actor=user,role="نقش مصوب آزمون",unit="واحد مصوب آزمون",required=True,
    )
    assert step.status=="PENDING"
    with pytest.raises(ValidationError):
        transition_signature_step(step=step,actor=user,new_status="SIGNED")

    transition_signature_step(step=step,actor=user,new_status="SENT")
    step.refresh_from_db()
    assert step.sent_at is not None and step.status=="SENT"
    transition_signature_step(step=step,actor=user,new_status="SIGNED",note="امضا دریافت شد")
    step.refresh_from_db();case.refresh_from_db()
    assert step.signed_at is not None and step.status=="SIGNED"
    assert case.state=="READY_APPROVAL"

    approval=final_approve(circulation=case,actor=user,note="تأیید نهایی")
    case.refresh_from_db()
    assert isinstance(approval,ContractFinalApproval)
    assert case.state=="APPROVED"


@pytest.mark.django_db
def test_contract_custody_never_silently_closes_open_transfer(circulation_context):
    user,space,beneficiary=circulation_context
    case=create_circulation(
        space=space,beneficiary=beneficiary,subject="گردش فیزیکی",operational_start_date="1405/07/01",
        next_action="ارسال",actor=user,
    )
    first=transfer_custody(
        circulation=case,actor=user,sender="املاک",receiver="حقوقی",unit="اداره حقوقی",
        purpose="امضا",next_action="بازگشت",due_date="1405/07/20",
    )
    assert current_custody(case)==first
    with pytest.raises(ValidationError):
        transfer_custody(
            circulation=case,actor=user,sender="حقوقی",receiver="مالی",unit="مالی",
            purpose="تأیید",next_action="بازگشت",
        )
    first.refresh_from_db()
    assert first.returned_at is None

    returned=return_custody(circulation=case,actor=user,note="از حقوقی بازگشت")
    assert returned.returned_at is not None
    second=transfer_custody(
        circulation=case,actor=user,sender="حقوقی",receiver="مالی",unit="مالی",
        purpose="تأیید",next_action="بازگشت",
    )
    assert current_custody(case)==second
    assert ContractCustodyTransfer.objects.filter(circulation=case).count()==2


@pytest.mark.django_db
def test_approved_circulation_converts_once_through_contract_rules(circulation_context):
    user,space,beneficiary=circulation_context
    case=create_circulation(
        space=space,beneficiary=beneficiary,subject="قرارداد رسمی",operational_start_date="1405/07/01",
        next_action="امضا",actor=user,
    )
    step=add_signature_step(circulation=case,actor=user,role="نقش مصوب",unit="واحد مصوب")
    transition_signature_step(step=step,actor=user,new_status="SENT")
    transition_signature_step(step=step,actor=user,new_status="SIGNED")
    final_approve(circulation=case,actor=user)

    contract=convert_to_contract(
        circulation=case,actor=user,
        values={
            "number":"OFF-8301","subject":"قرارداد رسمی","signed_date":"1405/07/10",
            "start_date":"1405/07/10","end_date":"1406/07/09","amount_rial":"1000000",
            "investment_commitment_rial":"","status":"معتبر","signed_state":"تأیید نهایی‌شده","notes":"",
        },
    )
    case.refresh_from_db()
    assert case.state=="CONVERTED"
    assert case.official_contract==contract
    assert contract.beneficiary==beneficiary and contract.space==space
    with pytest.raises(ValidationError):
        convert_to_contract(circulation=case,actor=user,values={"number":"OFF-2"})


@pytest.mark.django_db
def test_close_without_contract_requires_reason_and_preserves_audit(circulation_context):
    user,space,beneficiary=circulation_context
    case=create_circulation(
        space=space,beneficiary=beneficiary,subject="مختومه",operational_start_date="1405/07/01",
        next_action="بررسی",actor=user,
    )
    with pytest.raises(ValidationError):
        close_without_contract(circulation=case,actor=user,reason="")
    close_without_contract(circulation=case,actor=user,reason="عدم ادامه فرایند")
    case.refresh_from_db()
    assert case.state=="CLOSED_NO_CONTRACT" and case.close_reason=="عدم ادامه فرایند"
    assert AuditEvent.objects.filter(action="CONTRACT_CIRCULATION_CLOSE_NO_CONTRACT",entity_id=str(case.pk)).exists()


@pytest.mark.django_db
def test_contract_circulation_ui_is_visible_in_space_dossier(client,circulation_context):
    user,space,beneficiary=circulation_context
    client.force_login(user)
    response=client.post(f"/spaces/{space.code}/contract-circulations/new/",{
        "beneficiary":beneficiary.pk,"subject":"گردش UI","operational_start_date":"1405/07/01",
        "next_action":"امضا","due_date":"1405/08/01",
    })
    assert response.status_code==302
    case=ContractCirculation.objects.get()
    assert response.url.endswith(f"/contract-circulations/{case.pk}/")
    dossier=client.get(f"/spaces/{space.code}/").content.decode()
    assert case.identity in dossier
    assert "گردش قرارداد، امضا و رفت‌وبرگشت" in dossier
    registry=client.get("/records/contract-circulations/",{"q":case.identity})
    assert registry.status_code==200
    assert registry.context["page"].paginator.count==1
