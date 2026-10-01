import zipfile
from pathlib import Path
import pytest
from openpyxl import load_workbook
from import_pipeline.import_authorities import first_value, run
from domains.properties.models import MotherProperty, CommercialSpace
from domains.registry.models import RawCell, CanonicalField, Discrepancy
from domains.operations.models import Appraisal, Auction, DecisionOrder, UtilityObligation, SourceDocumentReference, TimelineEvent

ROOT=Path(__file__).parents[1]/'authority/inputs/1405-07-06'

def test_alternate_contract_and_appraisal_headings_are_not_dropped():
 row={'مبلغ با ارزش افزوده (ریال)':120,'مبلغ کارشناسی (ریال)':80,'نام کارشناس':'کارشناس دوم','مرجع نامه':'نامه ۲'}
 assert first_value(row,'مبلغ قرارداد با ارزش افزوده (ریال)','مبلغ با ارزش افزوده (ریال)')==120
 assert first_value(row,'مبلغ کارشناسی اجاره ماهانه (ریال)','مبلغ کارشناسی (ریال)')==80
 assert first_value(row,'نام کارشناس ارزیابی','نام کارشناس')=='کارشناس دوم'
 assert first_value(row,'شماره / مرجع نامه کارشناسی','مرجع نامه')=='نامه ۲'

@pytest.mark.django_db(transaction=True)
def test_complete_authority_import_is_lossless_and_typed(tmp_path):
 package=tmp_path/'بسته_به_روزرسانی_سه_اکسل_سما_6مهر.zip'
 package.write_bytes((ROOT/package.name).read_bytes())
 with zipfile.ZipFile(package) as archive:
  expected_nonempty=0
  for member in archive.infolist():
   name=member.filename.encode('cp437').decode('utf8')
   target=tmp_path/name; target.write_bytes(archive.read(member))
   workbook=load_workbook(target,read_only=True,data_only=True)
   expected_nonempty += sum(1 for sheet in workbook for row in sheet.iter_rows(values_only=True) for value in row if value not in (None,''))
 result=run(package)
 assert result['mother_properties']==225
 assert result['active_spaces']==350
 assert result['out_of_cycle_spaces']==151
 assert result['unique_spaces']==501
 assert MotherProperty.objects.values('identifier').distinct().count()==225
 assert CommercialSpace.objects.values('code').distinct().count()==501
 assert RawCell.objects.count()==expected_nonempty
 assert not CanonicalField.objects.filter(persian_label__regex=r'^ستون [0-9]+$').exists()
 assert Discrepancy.objects.filter(entity_type='CommercialSpace').exists()
 for model in (Appraisal,Auction,DecisionOrder,UtilityObligation,SourceDocumentReference,TimelineEvent):
  assert model.objects.exists(), model.__name__
