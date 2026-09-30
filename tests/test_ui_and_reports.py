import io,zipfile,pytest,hashlib
from django.contrib.auth import get_user_model
from openpyxl import load_workbook
from domains.properties.models import CommercialSpace
from reporting.engine import excel,docx,pdf
from domains.identity.models import SavedReport, ArchivedReportSnapshot, AuditEvent
@pytest.fixture
def user(db):return get_user_model().objects.create_user('u',password='A-very-safe-password')
@pytest.mark.django_db
def test_space_list_and_dossier(client,user):
 client.force_login(user);s=CommercialSpace.objects.create(code='9',name='فضای آزمون',status='ACTIVE',source_row=5,source_classification='authority')
 assert client.get('/spaces/').status_code==200
 body=client.get('/spaces/9/').content.decode();assert 'پرونده فضای 9' in body and 'الان دست کیه' in body and 'None' not in body

@pytest.mark.django_db
def test_advanced_space_filters_and_saved_view(client,user):
 from domains.properties.models import Region
 region=Region.objects.create(name='منطقه ۱')
 CommercialSpace.objects.create(code='A-10',name='فضای بزرگ',status='ACTIVE',area=100,region=region,address='تهران',source_row=1,source_classification='authority')
 CommercialSpace.objects.create(code='B-20',name='فضای کوچک',status='OUT_OF_CYCLE',area=20,source_row=2,source_classification='authority')
 client.force_login(user)
 response=client.get('/spaces/',{'code':'A','code_op':'starts','status':['ACTIVE'],'area_min':'50','address_presence':'nonempty'})
 assert response.status_code==200 and 'A-10' in response.content.decode() and 'B-20' not in response.content.decode()
 response=client.post('/spaces/filters/save/',{'name':'فضاهای منتخب','status':['ACTIVE'],'area_min':'50'})
 assert response.status_code==302
 from domains.identity.models import SavedFilter
 saved=SavedFilter.objects.get(owner=user);assert saved.definition=={'status':['ACTIVE'],'area_min':['50']}
 assert 'status=ACTIVE' in client.get(f'/spaces/filters/{saved.pk}/').url
@pytest.mark.django_db
def test_real_export_structures():
 s=CommercialSpace.objects.create(code='9',name='فضا',status='ACTIVE',source_row=5,source_classification='authority');qs=CommercialSpace.objects.all()
 x=load_workbook(io.BytesIO(excel(qs)));assert x.active.sheet_view.rightToLeft and x.active.auto_filter.ref
 with zipfile.ZipFile(io.BytesIO(docx(qs))) as z:assert 'word/document.xml' in z.namelist()
 assert pdf(qs).startswith(b'%PDF')

@pytest.mark.django_db
def test_saved_report_and_immutable_snapshot(client,user,settings,tmp_path):
 settings.MEDIA_ROOT=tmp_path
 CommercialSpace.objects.create(code='501',name='فضای مرجع',status='ACTIVE',source_row=2,source_classification='authority')
 client.force_login(user)
 response=client.post('/reports/save/',{'name':'فضاهای فعال','status':'ACTIVE','field':['code','status'],'blank':['اقدام']})
 assert response.status_code==302
 report=SavedReport.objects.get(owner=user)
 assert report.filters=={'status':'ACTIVE'} and report.fields==['code','status']
 assert client.get(f'/reports/{report.pk}/open/').url=='/spaces/?status=ACTIVE&field=code&field=status&blank=%D8%A7%D9%82%D8%AF%D8%A7%D9%85'
 assert client.post(f'/reports/{report.pk}/archive/').status_code==302
 snapshot=ArchivedReportSnapshot.objects.get(report=report);payload=snapshot.file.read()
 assert snapshot.row_count==1 and hashlib.sha256(payload).hexdigest()==snapshot.sha256
 assert snapshot.query_context['filters']=={'status':'ACTIVE'}
 assert AuditEvent.objects.filter(action='REPORT_DEFINITION_CREATE').exists()
 assert AuditEvent.objects.filter(action='REPORT_SNAPSHOT_CREATE').exists()
