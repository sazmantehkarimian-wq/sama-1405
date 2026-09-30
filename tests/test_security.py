import pytest
from django.contrib.auth import get_user_model
@pytest.mark.django_db
def test_password_is_hashed_and_anonymous_is_redirected(client):
 u=get_user_model().objects.create_user('secure',password='A-very-safe-password');assert u.password!='A-very-safe-password' and u.check_password('A-very-safe-password')
 response=client.get('/spaces/');assert response.status_code==302 and '/login/' in response.url
@pytest.mark.django_db
def test_csrf_blocks_unsafe_request():
 from django.test import Client
 client=Client(enforce_csrf_checks=True);assert client.post('/login/',{'username':'x','password':'x'}).status_code==403
@pytest.mark.django_db
def test_native_user_management_is_staff_only_and_audited(client):
 from domains.identity.models import UserProfile,AuditEvent
 User=get_user_model(); admin=User.objects.create_user('admin-test',password='A-very-safe-password',is_staff=True);UserProfile.objects.create(user=admin,display_name='مدیر',must_change_password=False)
 assert client.login(username='admin-test',password='A-very-safe-password')
 response=client.post('/users/create/',{'username':'new-operator','display_name':'کاربر جدید'},follow=True)
 assert response.status_code==200
 created=User.objects.get(username='new-operator');assert created.has_usable_password() and created.profile.must_change_password
 assert AuditEvent.objects.filter(action='USER_CREATE',entity_id=str(created.pk)).exists()
 response=client.post(f'/users/{created.pk}/toggle/',{'reason':'آزمون دسترسی'});created.refresh_from_db();assert response.status_code==302 and not created.is_active
 assert AuditEvent.objects.filter(action='USER_STATUS_CHANGE',entity_id=str(created.pk)).exists()
@pytest.mark.django_db
def test_operational_user_cannot_manage_users(client):
 user=get_user_model().objects.create_user('operator-test',password='A-very-safe-password');client.force_login(user)
 assert client.post('/users/create/',{'username':'forbidden','display_name':'ممنوع'}).status_code==302
 assert not get_user_model().objects.filter(username='forbidden').exists()
