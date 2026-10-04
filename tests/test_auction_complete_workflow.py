import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from domains.auctionflow.intake_models import AuctionContractDraft, AuctionParticipantProfile, AuctionProposalIntake
from domains.auctionflow.models import AuctionLotProfile, AuctionPeriodProfile
from domains.contracts.models import ContractCirculation
from domains.operations.models import AuctionLot, AuctionParticipant, AuctionPeriod, AuctionProposal
from domains.properties.models import CommercialSpace
from services.contract_circulation import add_signature_step, convert_to_contract, final_approve, transition_signature_step


@pytest.mark.django_db
def test_complete_manual_auction_award_to_signed_contract(client):
    user=get_user_model().objects.create_user('auction-complete',password='A-very-safe-password')
    client.force_login(user)
    space=CommercialSpace.objects.create(code='A-173',name='فضای مزایده کامل',status='ACTIVE',current_usage='تجاری',area=35,address='تهران')
    period=AuctionPeriod.objects.create(identity='AUC-COMPLETE-01',title='مزایده کامل',planned_date='1405/08/01',created_by=user)
    AuctionPeriodProfile.objects.create(period=period,duration_years=1)
    lot=AuctionLot.objects.create(period=period,space=space,entry_method='MANUAL',manual_reason='دستور رسمی آزمون',manual_reference='REF-01',added_by=user,readiness='READY')
    AuctionLotProfile.objects.create(lot=lot,template_family='COMMERCIAL',base_monthly_rent_rial=1000000,guarantee_amount_rial=5000000)

    response=client.post(f'/auctions/periods/{period.pk}/participants/new/',{
        'name':'برنده آزمون','identity_number':'0012345678','contact':'09120000000','kind':'NATURAL',
        'father_name':'علی','birth_certificate_number':'1234','birth_date':'1370/01/01','postal_code':'1234567890',
        'address':'تهران، نشانی آزمون','phone':'02112345678','mobile':'09120000000','legal_name':'',
        'registration_number':'','economic_code':'','representative_name':'','notes':'',
    })
    assert response.status_code==302
    participant=AuctionParticipant.objects.get(period=period)
    assert participant.identity_profile.address=='تهران، نشانی آزمون'

    response=client.post(f'/auctions/lots/{lot.pk}/proposals/new/',{
        'participant':participant.pk,'received_at':'2026-10-04T10:00','envelope_a_received':'on','envelope_b_received':'on',
        'envelope_c_received':'on','offered_amount_rial':'2500000','status':'VALID','receipt_number':'REC-100',
        'intake_notes':'تحویل دبیرخانه','envelope_b_decision':'ACCEPTED','c_opening_allowed':'1','decision_note':'مصوب جلسه',
    })
    assert response.status_code==302
    proposal=AuctionProposal.objects.get(lot=lot)
    assert proposal.intake.receipt_number=='REC-100'
    assert proposal.intake.c_opening_allowed is True

    response=client.post(f'/auctions/lots/{lot.pk}/winner/',{
        'winner_proposal_id':proposal.pk,'runner_up_proposal_id':'','decision_reference':'مصوبه کمیسیون ۱۲۳','decision_date':'1405/08/02',
    })
    assert response.status_code==302
    award=AuctionLotProfile.objects.get(lot=lot)
    assert award.winner_proposal_id==proposal.pk

    response=client.post(f'/auctions/lots/{lot.pk}/contract/start/',{
        'operational_start_date':'1405/08/03','due_date':'1405/08/15',
    })
    assert response.status_code==302
    award.refresh_from_db()
    case=award.contract_circulation
    draft=AuctionContractDraft.objects.get(lot=lot)
    assert draft.amount_rial==proposal.offered_amount_rial
    assert draft.start_date=='1405/08/03'
    assert draft.end_date=='1406/08/03'
    assert case.beneficiary.address=='تهران، نشانی آزمون'
    assert case.beneficiary.father_name=='علی'

    step=add_signature_step(circulation=case,actor=user,role='نقش مصوب',unit='واحد مصوب')
    transition_signature_step(step=step,actor=user,new_status='SENT')
    transition_signature_step(step=step,actor=user,new_status='SIGNED')
    final_approve(circulation=case,actor=user)
    contract=convert_to_contract(circulation=case,actor=user,values={
        'number':'AUC-CON-173','subject':draft.subject,'signed_date':'1405/08/03','start_date':draft.start_date,
        'end_date':'1406/08/02','amount_rial':str(draft.amount_rial),'investment_commitment_rial':'',
        'status':'معتبر','signed_state':'تأیید نهایی‌شده','notes':'منشأ: مزایده '+period.identity,
    })
    award.refresh_from_db();case.refresh_from_db()
    assert case.state==ContractCirculation.State.CONVERTED
    assert award.official_contract_id==contract.pk
    assert award.result_state==AuctionLotProfile.ResultState.CONTRACTED
