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
