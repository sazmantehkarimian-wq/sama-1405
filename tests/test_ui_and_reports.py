import io,zipfile,pytest
from django.contrib.auth import get_user_model
from openpyxl import load_workbook
from domains.properties.models import CommercialSpace
from reporting.engine import excel,docx,pdf
@pytest.fixture
def user(db):return get_user_model().objects.create_user('u',password='A-very-safe-password')
@pytest.mark.django_db
def test_space_list_and_dossier(client,user):
 client.force_login(user);s=CommercialSpace.objects.create(code='9',name='فضای آزمون',status='ACTIVE',source_row=5,source_classification='authority')
 assert client.get('/spaces/').status_code==200
 body=client.get('/spaces/9/').content.decode();assert 'پرونده فضای 9' in body and 'الان دست کیه' in body and 'None' not in body
@pytest.mark.django_db
def test_real_export_structures():
 s=CommercialSpace.objects.create(code='9',name='فضا',status='ACTIVE',source_row=5,source_classification='authority');qs=CommercialSpace.objects.all()
 x=load_workbook(io.BytesIO(excel(qs)));assert x.active.sheet_view.rightToLeft and x.active.auto_filter.ref
 with zipfile.ZipFile(io.BytesIO(docx(qs))) as z:assert 'word/document.xml' in z.namelist()
 assert pdf(qs).startswith(b'%PDF')
