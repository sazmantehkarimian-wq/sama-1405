import hashlib
import json
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import transaction
from django.utils import timezone

from domains.auctionflow.models import (
    AuctionDocumentInstance, AuctionLotProfile, AuctionOrganizationProfile, AuctionPeriodProfile,
)
from domains.contracts.models import Beneficiary
from domains.identity.models import AuditEvent
from domains.operations.models import AuctionLot, AuctionProposal, CommissionMember
from services.auction_pdf_contracts import render_contract_pdf
from services.auction_templates import render_docx_from_source, source_bytes, source_for
from services.contract_circulation import create_circulation
from services.documents import store_document


def _canonical(payload):
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(',', ':'), default=str).encode('utf-8')


def snapshot_hash(payload):
    return hashlib.sha256(_canonical(payload)).hexdigest()


def _raw(value):
    return str(value) if value not in (None, '') else ''


def _money(value):
    if value in (None, ''):
        return ''
    return f'{Decimal(value):,.0f}'


def ensure_profiles(period):
    period_profile, _ = AuctionPeriodProfile.objects.get_or_create(period=period)
    lot_profiles = []
    for lot in period.lots.select_related('space').all():
        profile, _ = AuctionLotProfile.objects.get_or_create(lot=lot)
        lot_profiles.append(profile)
    return period_profile, lot_profiles


def _beneficiary_payload(profile):
    beneficiary=profile.beneficiary
    if not beneficiary:
        return {}
    return {
        'id':beneficiary.pk,'kind':beneficiary.kind,'name':beneficiary.name,
        'first_name':beneficiary.first_name,'last_name':beneficiary.last_name,
        'father_name':beneficiary.father_name,'birth_certificate_number':beneficiary.birth_certificate_number,
        'birth_date':beneficiary.birth_date,'identity_number':beneficiary.identity_number,
        'legal_name':beneficiary.legal_name,'registration_number':beneficiary.registration_number,
        'economic_code':beneficiary.economic_code,'representative_name':beneficiary.representative_name,
        'mobile':beneficiary.mobile,'phone':beneficiary.phone,'address':beneficiary.address,'postal_code':beneficiary.postal_code,
    }


def _contract_payload(profile):
    contract=profile.official_contract
    if not contract:
        return {}
    return {
        'id':contract.pk,'number':contract.number,'subject':contract.subject,'signed_date':contract.signed_date,
        'start_date':contract.start_date,'end_date':contract.end_date,
        'amount_rial':_raw(contract.amount_rial),'monthly_amount':_money(contract.amount_rial),
        'investment_commitment_rial':_raw(contract.investment_commitment_rial),
        'status':contract.status,'signed_state':contract.signed_state,
    }


def build_lot_snapshot(lot):
    period_profile, _ = AuctionPeriodProfile.objects.get_or_create(period=lot.period)
    profile, _ = AuctionLotProfile.objects.get_or_create(lot=lot)
    organization=AuctionOrganizationProfile.objects.first()
    space = lot.space
    proposals = []
    for proposal in lot.proposals.select_related('participant').order_by('pk'):
        proposals.append({
            'proposal_id': proposal.pk,
            'participant_id': proposal.participant_id,
            'participant_name': proposal.participant.name,
            'identity_number': proposal.participant.identity_number,
            'contact': proposal.participant.contact,
            'envelope_a': proposal.envelope_a_received,
            'envelope_b': proposal.envelope_b_received,
            'envelope_c': proposal.envelope_c_received,
            'offered_amount_rial': _raw(proposal.offered_amount_rial),
            'status': proposal.status,
        })
    current_appraisal = space.appraisals.filter(is_current=True).order_by('-pk').first()
    active_members=list(CommissionMember.objects.filter(status=CommissionMember.Status.ACTIVE).order_by('sign_order','pk').values('name','position','role','sign_order'))
    return {
        'organization': {
            'organization_name': organization.organization_name if organization else '',
            'unit_title': organization.unit_title if organization else '',
            'official_address': organization.official_address if organization else '',
            'secretariat_address': organization.secretariat_address if organization else '',
            'phone': organization.phone if organization else '',
            'bank_name': organization.bank_name if organization else '',
            'bank_branch': organization.bank_branch if organization else '',
            'account_number': organization.account_number if organization else '',
            'iban': organization.iban if organization else '',
            'office_hours': organization.office_hours if organization else '',
            'submission_location': organization.submission_location if organization else '',
            'representative_name': organization.representative_name if organization else '',
            'representative_title': organization.representative_title if organization else '',
            'economic_code': organization.economic_code if organization else '',
            'national_id': organization.national_id if organization else '',
            'postal_code': organization.postal_code if organization else '',
        },
        'period': {
            'id': lot.period_id, 'identity': lot.period.identity, 'title': lot.period.title,
            'planned_date': lot.period.planned_date, 'state': lot.period.state,
            'permit_reference': period_profile.permit_reference, 'permit_date':period_profile.permit_date,
            'ad_day_name': period_profile.ad_day_name, 'ad_date': period_profile.ad_date,
            'newspaper': period_profile.newspaper, 'newspaper_page':period_profile.newspaper_page,
            'publication_media':period_profile.publication_media,
            'document_sales_start':period_profile.document_sales_start,'document_sales_end':period_profile.document_sales_end,
            'proposal_deadline':period_profile.proposal_deadline,'submission_day_name':period_profile.submission_day_name,
            'invitation_number': period_profile.invitation_number,'invitation_date':period_profile.invitation_date,
            'opening_session_date': period_profile.opening_session_date,'opening_day_name':period_profile.opening_day_name,
            'opening_session_time': period_profile.opening_session_time,
            'opening_session_location': period_profile.opening_session_location,
            'duration_years': period_profile.duration_years,'template_version':period_profile.template_version,
        },
        'lot': {
            'id': lot.pk, 'space_code': space.code, 'space_name': space.name,
            'region': space.region.name if getattr(space,'region_id',None) else '',
            'area': _raw(space.area), 'address': space.address, 'usage': space.current_usage,
            'proposed_activity': space.proposed_activity, 'activity_group': space.activity_group,
            'entry_method': lot.entry_method, 'readiness': lot.readiness,
            'template_family': profile.template_family,
            'base_monthly_rent_rial': _raw(profile.base_monthly_rent_rial),
            'base_monthly_rent_words':profile.base_monthly_rent_words,
            'guarantee_amount_rial': _raw(profile.guarantee_amount_rial),
            'guarantee_type':profile.guarantee_type,'grace_period':profile.grace_period,
            'investment_amount_rial': _raw(profile.investment_amount_rial),
            'investment_description':profile.investment_description,'proposed_job': profile.proposed_job,
            'transaction_level':profile.transaction_level,'location_description':profile.location_description,
            'coordination_phone':profile.coordination_phone,'coordination_person':profile.coordination_person,
            'decision_reference': profile.decision_reference, 'decision_date': profile.decision_date,
            'result_state': profile.result_state,
        },
        'current_appraisal': {
            'id': current_appraisal.pk if current_appraisal else None,
            'amount_rial': _raw(current_appraisal.amount_rial) if current_appraisal else '',
            'date': current_appraisal.appraisal_date if current_appraisal else '',
            'reference': current_appraisal.reference if current_appraisal else '',
            'response_date':current_appraisal.response_date if current_appraisal else '',
            'response_number':current_appraisal.response_number if current_appraisal else '',
        },
        'session_members':active_members,
        'proposals': proposals,
        'winner_proposal_id': profile.winner_proposal_id,
        'runner_up_proposal_id': profile.runner_up_proposal_id,
        'beneficiary': _beneficiary_payload(profile),
        'contract_circulation_id': profile.contract_circulation_id,
        'official_contract': _contract_payload(profile),
    }


def build_field_registry(snapshot):
    org=snapshot['organization']; period=snapshot['period']; lot=snapshot['lot']; appraisal=snapshot['current_appraisal']
    members=snapshot.get('session_members') or []
    fields={
        'ORG-001':org.get('organization_name',''),'ORG-002':org.get('unit_title',''),'ORG-003':org.get('official_address',''),
        'ORG-004':org.get('secretariat_address',''),'ORG-005':org.get('phone',''),'ORG-006':org.get('bank_name',''),
        'ORG-007':org.get('bank_branch',''),'ORG-008':org.get('account_number',''),'ORG-009':org.get('iban',''),
        'ORG-011':org.get('office_hours',''),'ORG-012':org.get('submission_location',''),
        'ORG-REP-NAME':org.get('representative_name',''),'ORG-REP-TITLE':org.get('representative_title',''),
        'AUC-001':period.get('identity',''),'AUC-002':period.get('title',''),'AUC-003':(period.get('planned_date') or '')[:4],
        'AUC-004':period.get('permit_reference',''),'AUC-005':period.get('permit_date',''),'AUC-006':period.get('ad_date',''),
        'AUC-007':period.get('newspaper',''),'AUC-008':period.get('newspaper_page',''),'AUC-009':period.get('publication_media',''),
        'AUC-010':period.get('document_sales_start',''),'AUC-011':period.get('document_sales_end',''),'AUC-012':period.get('proposal_deadline',''),
        'AUC-013':period.get('submission_day_name',''),'AUC-014':period.get('opening_session_date',''),'AUC-015':period.get('opening_day_name',''),
        'AUC-016':period.get('opening_session_time',''),'AUC-017':period.get('opening_session_location',''),
        'AUC-018':period.get('invitation_number',''),'AUC-019':period.get('invitation_date',''),
        'SPACE-001':lot.get('space_code',''),'SPACE-002':lot.get('space_name',''),'SPACE-003':lot.get('region',''),
        'SPACE-004':lot.get('usage') or lot.get('proposed_activity',''),'SPACE-005':lot.get('address',''),'SPACE-006':lot.get('area',''),
        'SPACE-007':lot.get('location_description',''),'SPACE-008':lot.get('coordination_phone',''),'SPACE-009':lot.get('coordination_person',''),
        'LOT-001':_money(lot.get('base_monthly_rent_rial')),'LOT-002':lot.get('base_monthly_rent_words',''),
        'LOT-003':_money(lot.get('guarantee_amount_rial')),'LOT-004':lot.get('guarantee_type',''),
        'LOT-005':str(period.get('duration_years') or ''),'LOT-006':lot.get('grace_period',''),
        'LOT-007':_money(lot.get('investment_amount_rial')),'LOT-008':lot.get('investment_description',''),
        'LOT-009':appraisal.get('date',''),'LOT-010':appraisal.get('reference',''),'LOT-011':appraisal.get('response_date',''),
        'LOT-012':appraisal.get('response_number',''),'LOT-013':lot.get('transaction_level',''),
        'SESSION-001':period.get('opening_session_date',''),'SESSION-002':period.get('opening_session_time',''),
        'SESSION-003':period.get('opening_session_location',''),
        'SESSION-004':'؛ '.join(f"{m['name']} — {m['position']}" for m in members),
        'PART-017':lot.get('proposed_job',''),
    }
    proposals=[]
    for item in snapshot.get('proposals') or []:
        proposals.append({
            'name':item.get('participant_name',''),'identity_number':item.get('identity_number',''),'contact':item.get('contact',''),
            'postal_code':'','birth_date':'','receipt_number':'','guarantee_amount':fields['LOT-003'],
            'offered_amount':_money(item.get('offered_amount_rial')),
        })
    fields['_SESSION_PROPOSALS']=proposals
    winner=next((p for p in snapshot.get('proposals',[]) if p.get('proposal_id')==snapshot.get('winner_proposal_id')),None)
    fields['_WINNER']={'name':winner.get('participant_name',''),'amount':_money(winner.get('offered_amount_rial'))} if winner else {}
    fields['_BENEFICIARY']=snapshot.get('beneficiary') or {}
    fields['_CONTRACT']=snapshot.get('official_contract') or {}
    return fields


def validate_winner_proposal(lot, proposal):
    if proposal.lot_id != lot.pk:
        raise ValidationError('پیشنهاد انتخاب‌شده متعلق به این فضای مزایده نیست.')
    missing = []
    if not proposal.envelope_a_received: missing.append('پاکت الف')
    if not proposal.envelope_b_received: missing.append('پاکت ب')
    if not proposal.envelope_c_received: missing.append('پاکت ج')
    if proposal.offered_amount_rial is None: missing.append('مبلغ پیشنهاد')
    if missing:
        raise ValidationError('تعیین برنده تا تکمیل این موارد مجاز نیست: ' + '، '.join(missing))


@transaction.atomic
def select_winner(*, lot, winner_proposal, runner_up_proposal=None, decision_reference, decision_date, actor, ip_address=None):
    profile, _ = AuctionLotProfile.objects.select_for_update().get_or_create(lot=lot)
    validate_winner_proposal(lot, winner_proposal)
    if runner_up_proposal:
        validate_winner_proposal(lot, runner_up_proposal)
        if runner_up_proposal.pk == winner_proposal.pk:
            raise ValidationError('برنده و نفر دوم نمی‌توانند یک پیشنهاد باشند.')
    if not (decision_reference or '').strip():
        raise ValidationError('مرجع تصمیم کمیسیون برای تعیین برنده الزامی است.')
    if not (decision_date or '').strip():
        raise ValidationError('تاریخ تصمیم کمیسیون برای تعیین برنده الزامی است.')
    profile.winner_proposal = winner_proposal
    profile.runner_up_proposal = runner_up_proposal
    profile.decision_reference = decision_reference.strip()
    profile.decision_date = decision_date.strip()
    profile.result_state = AuctionLotProfile.ResultState.AWARDED
    profile.awarded_by = actor
    profile.awarded_at = timezone.now()
    lot.winner_name = winner_proposal.participant.name
    lot.winning_amount_rial = winner_proposal.offered_amount_rial
    lot.result = 'برنده تعیین شد'
    lot.save(update_fields=['winner_name', 'winning_amount_rial', 'result'])
    profile.snapshot = build_lot_snapshot(lot)
    profile.save()
    AuditEvent.objects.create(
        actor=actor, action='AUCTION_WINNER_SELECTED', entity_type='AuctionLot', entity_id=str(lot.pk),
        after={'winner_proposal_id': winner_proposal.pk, 'runner_up_proposal_id': runner_up_proposal.pk if runner_up_proposal else None,
               'winner': winner_proposal.participant.name, 'amount_rial': str(winner_proposal.offered_amount_rial),
               'decision_reference': profile.decision_reference, 'decision_date': profile.decision_date}, ip_address=ip_address,
    )
    return profile


def _split_contact(contact):
    text = (contact or '').strip()
    return text if len(text) <= 20 else ''


@transaction.atomic
def start_contract_from_award(*, lot, actor, beneficiary_kind, operational_start_date, due_date='', ip_address=None):
    profile, _ = AuctionLotProfile.objects.select_for_update().get_or_create(lot=lot)
    if not profile.winner_proposal_id:
        raise ValidationError('ابتدا برنده مزایده را ثبت کنید.')
    if profile.contract_circulation_id:
        return profile.contract_circulation
    proposal = profile.winner_proposal
    validate_winner_proposal(lot, proposal)
    participant = proposal.participant
    beneficiary = None
    if participant.identity_number:
        beneficiary = Beneficiary.objects.filter(identity_number=participant.identity_number, archived_at__isnull=True).first()
    if not beneficiary:
        beneficiary = Beneficiary.objects.create(
            name=participant.name, identity_number=participant.identity_number, kind=beneficiary_kind,
            mobile=_split_contact(participant.contact), contact=participant.contact, created_by=actor,
        )
    circulation = create_circulation(
        space=lot.space, beneficiary=beneficiary,
        subject=f'انعقاد قرارداد برنده مزایده {lot.period.identity} — فضای {lot.space.code}',
        operational_start_date=operational_start_date,
        next_action='تکمیل تضامین، کنترل اسناد و گردش امضای قرارداد برنده مزایده',
        due_date=due_date, actor=actor, ip_address=ip_address,
    )
    profile.beneficiary = beneficiary
    profile.contract_circulation = circulation
    profile.result_state = AuctionLotProfile.ResultState.CONTRACTING
    profile.snapshot = build_lot_snapshot(lot)
    profile.save(update_fields=['beneficiary','contract_circulation','result_state','snapshot','updated_at'])
    AuditEvent.objects.create(actor=actor, action='AUCTION_CONTRACT_FLOW_STARTED', entity_type='AuctionLot', entity_id=str(lot.pk), after={'beneficiary_id': beneficiary.pk, 'contract_circulation_id': circulation.pk}, ip_address=ip_address)
    return circulation


@transaction.atomic
def sync_official_contract(*, circulation, actor=None, ip_address=None):
    try:
        profile = circulation.auction_award
    except AuctionLotProfile.DoesNotExist:
        return None
    if not circulation.official_contract_id:
        return profile
    if profile.official_contract_id != circulation.official_contract_id or profile.result_state != AuctionLotProfile.ResultState.CONTRACTED:
        profile.official_contract = circulation.official_contract
        profile.result_state = AuctionLotProfile.ResultState.CONTRACTED
        profile.snapshot = build_lot_snapshot(profile.lot)
        profile.save(update_fields=['official_contract','result_state','snapshot','updated_at'])
        if actor:
            AuditEvent.objects.create(actor=actor, action='AUCTION_CONTRACT_FINALIZED', entity_type='AuctionLot', entity_id=str(profile.lot_id), after={'contract_id': circulation.official_contract_id}, ip_address=ip_address)
    return profile


@transaction.atomic
def generate_controlled_document(*, lot, document_type, actor, ip_address=None):
    profile, _ = AuctionLotProfile.objects.get_or_create(lot=lot)
    if document_type == 'SAMPLE_CONTRACT' and not profile.winner_proposal_id:
        raise ValidationError('نمونه قرارداد تکمیل‌شده فقط پس از ثبت برنده قابل تولید است.')
    snapshot=build_lot_snapshot(lot)
    fields=build_field_registry(snapshot)
    source=source_for(document_type=document_type,family=profile.template_family)
    raw_source=source_bytes(source)
    if document_type == 'SAMPLE_CONTRACT':
        payload,extension=render_contract_pdf(source_bytes=raw_source,family=profile.template_family,fields=fields)
        mime='application/pdf'
    else:
        payload,extension=render_docx_from_source(source=source,document_type=document_type,fields=fields)
        mime='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    snap_hash=snapshot_hash(snapshot)
    output_sha=hashlib.sha256(payload).hexdigest()
    filename=f"auction-{lot.period.identity}-{lot.space.code}-{document_type.lower()}.{extension}"
    stored=store_document(
        uploaded=SimpleUploadedFile(filename,payload,content_type=mime),
        title=f'{AuctionDocumentInstance.DocumentType(document_type).label} — فضای {lot.space.code}',
        document_type=f'AUCTION_GENERATED_{document_type}', entity_type='AuctionLot', entity_id=lot.pk,
        user=actor, reference=lot.period.identity, document_date=lot.period.planned_date,
        notes=f'UAT_DRAFT; template={source.version}; source_sha={source.source_sha256}; snapshot={snap_hash}; output={output_sha}', ip_address=ip_address,
    )
    instance=AuctionDocumentInstance.objects.create(
        period=lot.period, lot=lot, document_type=document_type, template_family=profile.template_family,
        template_version=source.version, template_source=source, source_sha256=source.source_sha256,
        snapshot=snapshot, snapshot_sha256=snap_hash, document=stored, output_sha256=output_sha, generated_by=actor,
    )
    AuditEvent.objects.create(
        actor=actor,action='AUCTION_DOCUMENT_GENERATED',entity_type='AuctionLot',entity_id=str(lot.pk),
        after={'instance_id':instance.pk,'document_instance_id':instance.instance_id,'document_type':document_type,
               'template_source_id':source.pk,'template_version':instance.template_version,'source_sha256':instance.source_sha256,
               'snapshot_sha256':snap_hash,'output_sha256':output_sha,'status':instance.status},ip_address=ip_address,
    )
    return instance
