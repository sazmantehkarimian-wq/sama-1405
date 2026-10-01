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

@pytest.mark.django_db
def test_login_is_throttled_after_five_failures(client):
 from django.core.cache import cache
 cache.clear()
 payload={'username':'unknown-user','password':'wrong-password'}
 for _ in range(5): assert client.post('/login/',payload).status_code==200
 response=client.post('/login/',payload)
 assert response.status_code==429

@pytest.mark.django_db
def test_uat_fixed_admin_is_idempotent_and_cannot_change_or_reset_password(client,settings):
 settings.SAMA_UAT_FIXED_ADMIN=True;settings.SAMA_UAT_ADMIN_USERNAME='admin';settings.SAMA_UAT_ADMIN_PASSWORD='admin'
 from core.uat import provision_fixed_uat_admin
 first=provision_fixed_uat_admin();first.set_password('changed');first.save(update_fields=['password'])
 fixed=provision_fixed_uat_admin();assert fixed.check_password('admin') and fixed.is_superuser and fixed.is_active
 assert fixed.profile.must_change_password is False
 assert client.login(username='admin',password='admin')
 assert client.get('/account/password/').status_code==302
 assert client.post(f'/users/{fixed.pk}/reset/',{'reason':'test'}).status_code==302
 fixed.refresh_from_db();assert fixed.check_password('admin')
 body=client.get('/').content.decode();assert 'تغییر گذرواژه' not in body and 'اطلاعات حساب' in body
