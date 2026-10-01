from concurrent.futures import ThreadPoolExecutor
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client
from django.db import close_old_connections
import pytest
from domains.properties.models import CommercialSpace
from domains.operations.models import FileMovement, OperationalHistory
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
 assert b''.join(client.get(f'/documents/{document.pk}/download/').streaming_content)==b'%PDF-1.4\nproof'
 anonymous=Client();assert anonymous.get(f'/documents/{document.pk}/download/').status_code==302
 assert AuditEvent.objects.filter(action='FILE_MOVEMENT_CREATE').exists()
 assert AuditEvent.objects.filter(action='DOCUMENT_UPLOAD').exists()
 from domains.operations.models import TimelineEvent
 assert TimelineEvent.objects.filter(space=space,event_type='DOCUMENT_UPLOAD',document=document).exists()

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

@pytest.mark.django_db(transaction=True)
def test_five_authenticated_users_can_commit_independent_operational_writes():
 users=[get_user_model().objects.create_user(f'writer{i}',password='A-very-safe-password') for i in range(5)]
 spaces=[CommercialSpace.objects.create(code=f'WRITE-{i}',name='فضا',status='ACTIVE',source_row=i+1,source_classification='authority') for i in range(5)]
 clients=[]
 for user in users:
  client=Client();client.force_login(user);clients.append(client)
 def operation(pair):
  client,space=pair; close_old_connections()
  response=client.post(f'/spaces/{space.code}/workflows/',{'process_type':'FILE','title':'گردش هم‌زمان','next_action':'بررسی','due_date':'1405/07/20'})
  close_old_connections();return response.status_code
 with ThreadPoolExecutor(max_workers=5) as pool:results=list(pool.map(operation,zip(clients,spaces)))
 from domains.operations.models import WorkflowInstance
 assert results==[302]*5 and WorkflowInstance.objects.filter(title='گردش هم‌زمان').count()==5

@pytest.mark.django_db
def test_fee_utility_and_workflow_commands_validate_and_audit(client):
 from domains.operations.models import Appraisal,AppraisalFee,UtilityRecord,WorkflowInstance,TimelineEvent
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
 assert OperationalHistory.objects.filter(entity_type='AppraisalFee',action='CREATED').exists()
 assert OperationalHistory.objects.filter(entity_type='UtilityRecord',action='CREATED').exists()
 assert OperationalHistory.objects.filter(entity_type='WorkflowInstance',action='TRANSITION').exists()
 assert set(TimelineEvent.objects.filter(space=space).values_list('event_type',flat=True)) >= {'APPRAISAL_FEE_CREATE','UTILITY_RECORD_CREATE','WORKFLOW_TRANSITION'}

@pytest.mark.django_db
def test_operational_workflow_commission_and_alert_lifecycles(client):
 from domains.operations.models import Alert, CommissionDecision, WorkflowInstance, TimelineEvent
 user=get_user_model().objects.create_user('operator3',password='A-very-safe-password')
 space=CommercialSpace.objects.create(code='503',name='فضا',status='ACTIVE',source_row=2,source_classification='authority')
 client.force_login(user)
 response=client.post('/spaces/503/workflows/',{'process_type':'APPRAISAL','title':'کارشناسی جدید','next_action':'ارجاع به کارشناس','due_date':'1405/08/01'})
 assert response.status_code==302 and WorkflowInstance.objects.filter(space=space,process_type='APPRAISAL').exists()
 decision=CommissionDecision.objects.create(identity='C-1',decision_date='1405/07/01',subject='واگذاری',decision='موافقت')
 decision.spaces.add(space)
 response=client.post(f'/commissions/{decision.pk}/transition/',{'state':'APPROVED','subsequent_action':'ابلاغ','reason':'تصویب جلسه'})
 decision.refresh_from_db();assert response.status_code==302 and decision.state=='APPROVED'
 alert=Alert.objects.create(space=space,subject='پیگیری',reason='سررسید',status='OPEN',target_url='/spaces/503/')
 response=client.post(f'/alerts/{alert.pk}/resolve/',{'reason':'اقدام و ثبت نامه'})
 alert.refresh_from_db();assert response.status_code==302 and alert.status=='RESOLVED'
 assert set(AuditEvent.objects.values_list('action',flat=True)) >= {'WORKFLOW_CREATE','COMMISSION_TRANSITION','ALERT_RESOLVE'}
 assert set(TimelineEvent.objects.filter(space=space).values_list('event_type',flat=True)) >= {'WORKFLOW_CREATE','COMMISSION_TRANSITION','ALERT_RESOLVE'}

@pytest.mark.django_db
def test_commission_workspace_creates_linked_audited_decision(client):
 user=get_user_model().objects.create_user('commission-operator',password='A-very-safe-password')
 spaces=[CommercialSpace.objects.create(code=f'C-{i}',name='فضا',status='ACTIVE',source_row=i,source_classification='authority') for i in (1,2)]
 client.force_login(user)
 response=client.post('/commissions/create/',{'identity':'جلسه-۱۴۰۵-۱','decision_date':'۱۴۰۵/۰۷/۰۸','subject':'واگذاری','space_codes':'C-1، C-2','participants':'الف، ب','decision':'تصویب شد','subsequent_action':'ابلاغ'})
 from domains.operations.models import CommissionDecision
 record=CommissionDecision.objects.get(identity='جلسه-۱۴۰۵-۱')
 assert response.status_code==302 and set(record.spaces.all())==set(spaces)
 assert AuditEvent.objects.filter(action='COMMISSION_CREATE',entity_id=str(record.pk)).exists()
 assert OperationalHistory.objects.filter(entity_type='CommissionDecision',entity_id=str(record.pk),action='CREATED').exists()

@pytest.mark.django_db
def test_auction_workspace_evaluates_and_adds_candidate_to_draft_period(client):
 from domains.operations.models import Appraisal,AuctionRule,AuctionPeriod,AuctionLot,TimelineEvent
 from domains.registry.models import ImportBatch,SourceFile
 user=get_user_model().objects.create_user('auction-operator',password='A-very-safe-password')
 client.force_login(user)
 space=CommercialSpace.objects.create(code='A-1',name='فضا',status='ACTIVE',source_row=1,source_classification='authority')
 batch=ImportBatch.objects.create(source_package='test.zip',package_sha256='a'*64)
 source=SourceFile.objects.create(batch=batch,filename='source.xlsx',sha256='b'*64,byte_size=1)
 Appraisal.objects.create(space=space,amount_rial=500000,appraisal_date='1405/06/01',source_file=source,source_row=2)
 AuctionRule.objects.create(version='clean-1',effective_year=1405,minor_ceiling_rial=100000,medium_ceiling_rial=1000000,active=True,change_reason='مصوب',approved_by=user)
 assert client.post('/auctions/evaluate/',{'space_code':'A-1','on_date':'1405/07/01','auction_date':'1405/08/01'}).status_code==302
 evaluation=space.auction_evaluations.get(); assert evaluation.decision=='CANDIDATE'
 assert client.post('/auctions/periods/create/',{'identity':'P-1','title':'دوره اول','planned_date':'1405/08/01'}).status_code==302
 period=AuctionPeriod.objects.get(identity='P-1')
 assert client.post(f'/auctions/periods/{period.pk}/lots/',{'evaluation_id':evaluation.pk}).status_code==302
 assert AuctionLot.objects.filter(period=period,space=space,evaluation=evaluation).exists()
 assert set(TimelineEvent.objects.filter(space=space).values_list('event_type',flat=True)) >= {'AUCTION_EVALUATE','AUCTION_LOT_ADD'}
 assert set(AuditEvent.objects.values_list('action',flat=True)) >= {'AUCTION_EVALUATE','AUCTION_PERIOD_CREATE','AUCTION_LOT_ADD'}

@pytest.mark.django_db
def test_post_go_live_contract_appraisal_amendment_and_alert_are_typed_and_audited(client):
 from domains.contracts.models import Contract,BeneficiaryAssignment,ContractAmendment
 from domains.operations.models import Appraisal,Alert,TimelineEvent
 user=get_user_model().objects.create_user('daily-operator',password='A-very-safe-password')
 space=CommercialSpace.objects.create(code='OPS-1',name='فضا',status='ACTIVE',source_row=1,source_classification='authority')
 client.force_login(user)
 contract_payload={'number':'C-1405-1','beneficiary':'بهره‌بردار واقعی','signed_date':'1405/07/02','start_date':'1405/07/01','end_date':'1406/06/31','amount_rial':'1,200,000','status':'فعال','signed_state':'امضاءشده'}
 assert client.post('/spaces/OPS-1/contracts/',contract_payload).status_code==302
 contract=Contract.objects.get(number='C-1405-1');assert not contract.is_historical and contract.created_by==user
 assert BeneficiaryAssignment.objects.filter(space=space,beneficiary=contract.beneficiary,created_by=user).exists()
 assert client.post(f'/contracts/{contract.pk}/amendments/',{'number':'A-1','effective_date':'1405/08/01','amount_change_rial':'100000','description':'تمدید تعهد'}).status_code==302
 assert ContractAmendment.objects.filter(contract=contract,number='A-1').exists()
 assert client.post('/spaces/OPS-1/appraisals/',{'appraiser':'کارشناس رسمی','appraisal_date':'1405/07/03','amount_rial':'2000000','reference':'نامه ۱','status':'معتبر'}).status_code==302
 assert Appraisal.objects.filter(space=space,created_by=user,source_file__isnull=True).exists()
 assert client.post('/spaces/OPS-1/alerts/',{'subject':'پیگیری امضا','reason':'نسخه امضاشده دریافت شود','due_date':'1405/07/20'}).status_code==302
 assert Alert.objects.filter(space=space,status='OPEN').exists()
 assert set(AuditEvent.objects.values_list('action',flat=True)) >= {'CONTRACT_CREATE','CONTRACT_AMENDMENT_CREATE','APPRAISAL_CREATE','ALERT_CREATE'}
 assert TimelineEvent.objects.filter(space=space,event_type='CONTRACT_CREATE').exists()
 assert client.post('/spaces/OPS-1/status/',{'new_state':'OUT_OF_CYCLE','effective_date':'1405/09/01','reason':'تصمیم مصوب'}).status_code==302
 space.refresh_from_db();assert space.status=='OUT_OF_CYCLE'
 history=space.status_history.latest('id');assert history.previous_state=='ACTIVE' and history.responsible_user==user
 assert TimelineEvent.objects.filter(space=space,event_type='SPACE_STATUS_TRANSITION',previous_state='ACTIVE',new_state='OUT_OF_CYCLE').exists()
