from concurrent.futures import ThreadPoolExecutor
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client
from django.db import close_old_connections
import pytest
from domains.properties.models import CommercialSpace
from domains.operations.models import FileMovement
from domains.documents.models import Document
from domains.identity.models import AuditEvent

@pytest.mark.django_db(transaction=True)
def test_document_and_file_movement_are_server_side_audited(client,tmp_path,settings):
 settings.MEDIA_ROOT=tmp_path
 user=get_user_model().objects.create_user('operator',password='A-very-safe-password')
 space=CommercialSpace.objects.create(code='501',name='فضا',status='ACTIVE',source_row=5,source_classification='authority')
 client.force_login(user)
 response=client.post('/spaces/501/movement/',{'location':'بایگانی','holder':'کارشناس','delivered_by':'الف','received_by':'ب','signature_state':'امضاء شد','direction':'OUT','due_date':'۱۴۰۵/۰۷/۰۱'})
 assert response.status_code==302 and FileMovement.objects.filter(space=space,holder='کارشناس').exists()
 upload=SimpleUploadedFile('evidence.pdf',b'%PDF-1.4\nproof',content_type='application/pdf')
 response=client.post('/spaces/501/documents/',{'title':'مدرک','document_type':'نامه','file':upload})
 assert response.status_code==302
 document=Document.objects.get();assert document.sha256 and document.file.storage.exists(document.file.name)
 assert AuditEvent.objects.filter(action='FILE_MOVEMENT_CREATE').exists()
 assert AuditEvent.objects.filter(action='DOCUMENT_UPLOAD').exists()

@pytest.mark.django_db(transaction=True)
def test_five_authenticated_users_can_read_search_and_generate_reports():
 users=[get_user_model().objects.create_user(f'user{i}',password='A-very-safe-password') for i in range(5)]
 for i in range(20):CommercialSpace.objects.create(code=str(i+1),name=f'فضای {i+1}',status='ACTIVE',source_row=i+5,source_classification='authority')
 clients=[]
 for user in users:
  client=Client();client.force_login(user);clients.append(client)
 def operation(client):
  close_old_connections()
  results=(client.get('/spaces/?q=فضا').status_code,client.get('/reports/spaces.xlsx?status=ACTIVE&field=code&field=name').status_code,client.get('/spaces/1/').status_code)
  close_old_connections();return results
 with ThreadPoolExecutor(max_workers=5) as pool:results=list(pool.map(operation,clients))
 assert results==[(200,200,200)]*5

@pytest.mark.django_db
def test_fee_utility_and_workflow_commands_validate_and_audit(client):
 from domains.operations.models import Appraisal,AppraisalFee,UtilityRecord,WorkflowInstance
 from domains.registry.models import ImportBatch,SourceFile
 user=get_user_model().objects.create_user('operator2',password='A-very-safe-password')
 client.force_login(user)
 batch=ImportBatch.objects.create(source_package='test.zip',package_sha256='a'*64)
 source=SourceFile.objects.create(batch=batch,filename='source.xlsx',sha256='b'*64,byte_size=1)
 space=CommercialSpace.objects.create(code='502',name='فضا',status='ACTIVE',source_row=2,source_classification='authority')
 appraisal=Appraisal.objects.create(space=space,amount_rial=100,source_file=source,source_row=3)
 response=client.post(f'/appraisals/{appraisal.pk}/fee/',{'amount_rial':'1200000','payment_status':'PENDING','follow_up_date':'1405/07/20'})
 assert response.status_code==302 and AppraisalFee.objects.get(appraisal=appraisal).amount_rial==1200000
 payload={'utility_type':'WATER','account_number':'123','period_start':'1405/07/01','period_end':'1405/07/30','bill_amount_rial':'1000','organization_share_rial':'400','beneficiary_share_rial':'500','calculation_basis':'قرائت کنتور','payment_status':'UNPAID'}
 assert client.post('/spaces/502/utilities/',payload).status_code==302
 assert UtilityRecord.objects.count()==0
 payload['beneficiary_share_rial']='600'
 assert client.post('/spaces/502/utilities/',payload).status_code==302
 assert UtilityRecord.objects.get().bill_amount_rial==1000
 workflow=WorkflowInstance.objects.create(space=space,process_type='CONTRACT',title='پیگیری',next_action='امضا',created_by=user)
 response=client.post(f'/workflows/{workflow.pk}/transition/',{'state':'DONE','next_action':'','due_date':'1405/07/20'})
 workflow.refresh_from_db()
 assert response.status_code==302 and workflow.state=='DONE' and workflow.closed_at
 assert set(AuditEvent.objects.values_list('action',flat=True)) >= {'APPRAISAL_FEE_CREATE','UTILITY_RECORD_CREATE','WORKFLOW_TRANSITION'}
