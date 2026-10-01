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

@pytest.mark.django_db(transaction=True)
def test_fixed_uat_admin_owner_login_and_management_lock_in_browser(live_server, settings):
 settings.SAMA_UAT_FIXED_ADMIN=True;settings.SAMA_UAT_ADMIN_USERNAME='admin';settings.SAMA_UAT_ADMIN_PASSWORD='admin'
 from core.uat import provision_fixed_uat_admin
 from playwright.sync_api import sync_playwright
 fixed=provision_fixed_uat_admin()
 with sync_playwright() as playwright:
  browser=playwright.chromium.launch(headless=True);page=browser.new_page(viewport={'width':1366,'height':768})
  page.goto(f'{live_server.url}/login/');page.get_by_label('نام کاربری').fill('admin');page.get_by_label('گذرواژه').fill('admin');page.get_by_role('button',name='ورود').click()
  assert page.url.rstrip('/')==live_server.url
  page.locator('.account summary').click();assert page.get_by_role('link',name='تغییر گذرواژه').count()==0
  page.goto(f'{live_server.url}/users/');row=page.locator('tr',has_text='admin')
  assert row.get_by_text('مدیر ثابت UAT').is_visible()
  assert row.get_by_role('button',name='بازنشانی گذرواژه').count()==0
  assert row.get_by_role('button',name='غیرفعال‌سازی').count()==0
  browser.close()
 fixed.refresh_from_db();assert fixed.username=='admin' and fixed.check_password('admin') and fixed.is_active and not fixed.profile.must_change_password
