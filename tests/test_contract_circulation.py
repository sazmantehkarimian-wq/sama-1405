import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from domains.contracts.models import Beneficiary,ContractSignatureStep,ContractCustodyTransfer
from domains.properties.models import CommercialSpace
from services.contract_circulation import create_circulation,transfer,return_custody,current_custody,final_approve,convert_to_contract
pytestmark=pytest.mark.django_db
@pytest.fixture
def setup():
 user=get_user_model().objects.create_user('operator');space=CommercialSpace.objects.create(code='1',name='آزمایش',status='ACTIVE',source_row=1,source_classification='AUTHORITY');party=Beneficiary.objects.create(name='شخص معتبر')
 return user,space,party

def test_circulation_is_separate_and_respects_operational_start(setup):
 user,space,party=setup
 with pytest.raises(ValidationError):create_circulation(space=space,beneficiary=party,subject='الف',operational_start_date='1405/06/31',next_action='بررسی',actor=user)
 case=create_circulation(space=space,beneficiary=party,subject='الف',operational_start_date='1405/07/01',next_action='بررسی',actor=user)
 assert case.official_contract_id is None and space.contracts.count()==0

def test_custody_integrity_and_repeated_round_trips(setup):
 user,space,party=setup;case=create_circulation(space=space,beneficiary=party,subject='الف',operational_start_date='1405/07/01',next_action='ارسال',actor=user)
 with pytest.raises(ValidationError):return_custody(circulation=case,actor=user)
 first=transfer(circulation=case,sender='الف',receiver='ب',unit='حقوقی',purpose='امضا',next_action='بازگشت',delivered_at=timezone.now(),actor=user)
 assert current_custody(case)==first
 with pytest.raises(ValidationError):transfer(circulation=case,sender='الف',receiver='ج',unit='مالی',purpose='امضا',next_action='بازگشت',delivered_at=timezone.now(),actor=user)
 return_custody(circulation=case,actor=user);second=transfer(circulation=case,sender='ب',receiver='ج',unit='مالی',purpose='اصلاح',next_action='بازگشت',delivered_at=timezone.now(),actor=user)
 assert case.transfers.count()==2 and current_custody(case)==second

def test_signatures_and_final_approval_gate_official_contract(setup):
 user,space,party=setup;case=create_circulation(space=space,beneficiary=party,subject='الف',operational_start_date='1405/07/01',next_action='امضا',actor=user,signature_steps=[{'role':'نقش مصوب','unit':'واحد مصوب'}]);step=case.signature_steps.get()
 with pytest.raises(ValidationError):final_approve(circulation=case,actor=user)
 with pytest.raises(ValidationError):convert_to_contract(circulation=case,number='1',start_date='1405/07/01',end_date='1406/06/31',amount_rial=0,actor=user)
 step.status=ContractSignatureStep.Status.SIGNED;step.signed_at=timezone.now();step.save();final_approve(circulation=case,actor=user)
 contract=convert_to_contract(circulation=case,number='1',start_date='1405/07/01',end_date='1406/06/31',amount_rial=0,actor=user)
 assert not contract.is_historical and contract.amount_rial==0 and contract.source_circulation==case
