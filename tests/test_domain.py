import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from domains.properties.models import CommercialSpace
from domains.operations.models import FileMovement
from services.file_movement import current_holder
from services.dates import normalize_jalali
from services.money import format_rial
@pytest.mark.django_db
def test_current_holder_is_derived_from_open_movement():
 u=get_user_model().objects.create_user('operator',password='A-very-safe-password')
 s=CommercialSpace.objects.create(code='T-1',name='Test',status='ACTIVE',source_row=1,source_classification='test')
 FileMovement.objects.create(space=s,location='بایگانی',holder='کارشناس',delivered_by='الف',received_by='ب',handover_at=timezone.now(),signature_state='امضاء شده',direction='OUT',created_by=u)
 assert current_holder(s).holder=='کارشناس'
def test_jalali_and_money_services():
 assert normalize_jalali('۱۴۰۵-۷-۱')=='1405/07/01'
 with pytest.raises(ValueError):normalize_jalali('14051405/01/15')
 assert format_rial(1234567)=='1,234,567 ریال'
