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
