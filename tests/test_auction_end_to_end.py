import hashlib
import io

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.utils import timezone
from docx import Document as DocxDocument

from domains.auctionflow.models import AuctionDocumentInstance, AuctionLotProfile, AuctionTemplateSource
from domains.contracts.models import Beneficiary, ContractCirculation
from domains.operations.models import AuctionLot, AuctionParticipant, AuctionPeriod, AuctionProposal
from domains.properties.models import CommercialSpace
from services.auction_flow import (
    build_lot_snapshot, generate_controlled_document, select_winner,
    snapshot_hash, start_contract_from_award,
)
from services.documents import store_document


class AuctionEndToEndTests(TestCase):
    def setUp(self):
        self.user=User.objects.create_user(username='owner-test',password='x')
        self.space=CommercialSpace.objects.create(code='173',name='فضای آزمون',status=CommercialSpace.Status.ACTIVE,current_usage='تجاری',area=25,address='تهران')
        self.period=AuctionPeriod.objects.create(identity='AUC-1405-01',title='مزایده آزمون',planned_date='1405/08/01',created_by=self.user)
        self.lot=AuctionLot.objects.create(period=self.period,space=self.space,entry_method=AuctionLot.EntryMethod.MANUAL,manual_reason='تصمیم مجاز',manual_reference='نامه ۱',added_by=self.user,readiness='READY')
        self.p1=AuctionParticipant.objects.create(period=self.period,name='شرکت‌کننده اول',identity_number='0012345678',contact='09120000000')
        self.p2=AuctionParticipant.objects.create(period=self.period,name='شرکت‌کننده دوم',identity_number='0012345679',contact='09121111111')
        self.q1=AuctionProposal.objects.create(lot=self.lot,participant=self.p1,received_at=timezone.now(),envelope_a_received=True,envelope_b_received=True,envelope_c_received=True,offered_amount_rial=1000000,status='VALID')
        self.q2=AuctionProposal.objects.create(lot=self.lot,participant=self.p2,received_at=timezone.now(),envelope_a_received=True,envelope_b_received=True,envelope_c_received=True,offered_amount_rial=2000000,status='VALID')

    def _install_test_envelope_master(self):
        doc=DocxDocument()
        for text in ['عنوان','زیرعنوان','موضوع','نشانی','کاربری']:
            doc.add_paragraph(text)
        out=io.BytesIO();doc.save(out);payload=out.getvalue()
        sha=hashlib.sha256(payload).hexdigest()
        stored=store_document(
            uploaded=SimpleUploadedFile('envelope-master.docx',payload,content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'),
            title='Master test envelope',document_type='AUCTION_TEMPLATE_SOURCE',entity_type='AuctionTemplateSource',entity_id='GENERAL:ENVELOPE_COVER:test-v1',user=self.user,
        )
        return AuctionTemplateSource.objects.create(
            family=AuctionTemplateSource.Family.GENERAL,kind=AuctionTemplateSource.Kind.ENVELOPE_COVER,
            version='test-v1',source_filename='envelope-master.docx',source_sha256=sha,
            source_document=stored,active=True,imported_by=self.user,
        )

    def test_winner_is_explicit_not_highest_bid(self):
        profile=select_winner(lot=self.lot,winner_proposal=self.q1,runner_up_proposal=self.q2,decision_reference='مصوبه ۱۲۳',decision_date='1405/08/02',actor=self.user)
        self.assertEqual(profile.winner_proposal_id,self.q1.pk)
        self.assertEqual(profile.runner_up_proposal_id,self.q2.pk)
        self.lot.refresh_from_db()
        self.assertEqual(self.lot.winner_name,'شرکت‌کننده اول')
        self.assertEqual(self.lot.winning_amount_rial,self.q1.offered_amount_rial)

    def test_incomplete_envelopes_block_winner(self):
        self.q1.envelope_c_received=False
        self.q1.save(update_fields=['envelope_c_received'])
        with self.assertRaises(ValidationError):
            select_winner(lot=self.lot,winner_proposal=self.q1,decision_reference='مصوبه',decision_date='1405/08/02',actor=self.user)

    def test_award_creates_beneficiary_and_contract_circulation(self):
        select_winner(lot=self.lot,winner_proposal=self.q1,decision_reference='مصوبه ۱۲۳',decision_date='1405/08/02',actor=self.user)
        circulation=start_contract_from_award(lot=self.lot,actor=self.user,beneficiary_kind=Beneficiary.Kind.NATURAL,operational_start_date='1405/08/03',due_date='1405/08/10')
        self.assertEqual(ContractCirculation.objects.count(),1)
        self.assertEqual(circulation.space,self.space)
        self.assertEqual(circulation.beneficiary.name,self.p1.name)
        profile=AuctionLotProfile.objects.get(lot=self.lot)
        self.assertEqual(profile.contract_circulation_id,circulation.pk)
        self.assertEqual(profile.result_state,AuctionLotProfile.ResultState.CONTRACTING)

    def test_snapshot_hash_is_stable(self):
        first=build_lot_snapshot(self.lot)
        second=build_lot_snapshot(self.lot)
        self.assertEqual(snapshot_hash(first),snapshot_hash(second))

    def test_document_generation_is_blocked_without_master_source(self):
        with self.assertRaises(ValidationError):
            generate_controlled_document(lot=self.lot,document_type=AuctionDocumentInstance.DocumentType.PRICE_FORM,actor=self.user)
        self.assertEqual(AuctionDocumentInstance.objects.count(),0)

    def test_controlled_docx_is_source_versioned_and_fully_hashed(self):
        source=self._install_test_envelope_master()
        profile,_=AuctionLotProfile.objects.get_or_create(lot=self.lot)
        profile.base_monthly_rent_rial=500000
        profile.guarantee_amount_rial=6000000
        profile.save()
        instance=generate_controlled_document(lot=self.lot,document_type=AuctionDocumentInstance.DocumentType.PRICE_FORM,actor=self.user)
        self.assertEqual(instance.status,AuctionDocumentInstance.Status.UAT_DRAFT)
        self.assertEqual(instance.template_source_id,source.pk)
        self.assertEqual(instance.source_sha256,source.source_sha256)
        self.assertEqual(len(instance.snapshot_sha256),64)
        self.assertEqual(len(instance.output_sha256),64)
        self.assertTrue(instance.document.original_filename.endswith('.docx'))
        self.assertGreater(instance.document.byte_size,1000)
