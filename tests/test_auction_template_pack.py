import hashlib
import io
import zipfile
from unittest.mock import patch

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from domains.auctionflow.models import AuctionTemplateSource
from services import auction_templates


class AuctionTemplatePackTests(TestCase):
    def setUp(self):
        self.user=User.objects.create_user(username='template-owner',password='x')
        self.conditions=b'controlled-condition-master'
        self.contract=b'%PDF-1.4\ncontrolled-contract-master\n%%EOF'
        self.manifest={
            'conditions.docx':('COMMERCIAL','CONDITIONS',hashlib.sha256(self.conditions).hexdigest()),
            'contract.pdf':('COMMERCIAL','SAMPLE_CONTRACT',hashlib.sha256(self.contract).hexdigest()),
        }

    def _zip(self, files):
        out=io.BytesIO()
        with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as archive:
            for name,data in files.items():
                archive.writestr(name,data)
        return SimpleUploadedFile('reference.zip',out.getvalue(),content_type='application/zip')

    def test_valid_pinned_pack_registers_template_sources(self):
        uploaded=self._zip({'nested/conditions.docx':self.conditions,'nested/contract.pdf':self.contract})
        with patch.object(auction_templates,'REFERENCE_FILES',self.manifest):
            created=auction_templates.import_reference_pack(uploaded=uploaded,actor=self.user)
        self.assertEqual(len(created),2)
        self.assertEqual(AuctionTemplateSource.objects.count(),2)
        condition=AuctionTemplateSource.objects.get(kind='CONDITIONS')
        self.assertEqual(condition.source_sha256,self.manifest['conditions.docx'][2])
        self.assertTrue(condition.active)
        self.assertFalse(condition.is_golden_master)

    def test_changed_reference_file_is_rejected(self):
        uploaded=self._zip({'conditions.docx':b'tampered','contract.pdf':self.contract})
        with patch.object(auction_templates,'REFERENCE_FILES',self.manifest):
            with self.assertRaises(ValidationError):
                auction_templates.import_reference_pack(uploaded=uploaded,actor=self.user)
        self.assertEqual(AuctionTemplateSource.objects.count(),0)

    def test_missing_reference_file_is_rejected(self):
        uploaded=self._zip({'conditions.docx':self.conditions})
        with patch.object(auction_templates,'REFERENCE_FILES',self.manifest):
            with self.assertRaises(ValidationError):
                auction_templates.import_reference_pack(uploaded=uploaded,actor=self.user)
        self.assertEqual(AuctionTemplateSource.objects.count(),0)
