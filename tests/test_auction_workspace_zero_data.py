import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse


@pytest.mark.django_db
def test_zero_data_auction_workspace_renders_without_operational_rows(client):
    user = get_user_model().objects.create_user("auction-ui", password="safe-password")
    client.force_login(user)

    response = client.get(reverse("auction-workspace"))

    assert response.status_code == 200
    body = response.content.decode("utf-8")
    assert "مدیریت مزایده" in body
    assert "ایجاد دوره مزایده" in body
    assert "دوره" in body
