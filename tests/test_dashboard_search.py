import pytest
from django.contrib.auth import get_user_model

from domains.contracts.models import Beneficiary, Contract
from domains.operations.models import Appraiser
from domains.properties.models import CommercialSpace


@pytest.fixture
def dashboard_user(db):
    return get_user_model().objects.create_user("dashboard-search", password="A-very-safe-password")


@pytest.mark.django_db
def test_dashboard_zero_data_is_healthy_and_has_global_search(client, dashboard_user):
    client.force_login(dashboard_user)
    response=client.get("/")
    assert response.status_code==200
    body=response.content.decode()
    assert "جست‌وجوی سراسری" in body
    assert "آخرین محاسبه" in body
    assert "مغایرت‌های واردات" not in body
    assert response.context["active_count"]==0
    assert response.context["inactive_count"]==0


@pytest.mark.django_db
def test_global_search_is_categorized_and_links_to_record_profiles(client, dashboard_user):
    client.force_login(dashboard_user)
    space=CommercialSpace.objects.create(code="177",name="مرکز جست‌وجو",status="ACTIVE")
    beneficiary=Beneficiary.objects.create(kind="LEGAL",name="شرکت هنر",legal_name="شرکت هنر")
    Contract.objects.create(
        space=space,beneficiary=beneficiary,number="CTR-177",
        start_date="1405/01/01",end_date="1405/12/29",
    )
    expert=Appraiser.objects.create(first_name="سارا",last_name="ارزیاب",license_number="EXP-LIC-177")

    by_space=client.get("/search/",{"q":"177"})
    assert by_space.status_code==200
    body=by_space.content.decode()
    assert "فضای 177" in body
    assert "CTR-177" in body

    by_beneficiary=client.get("/search/",{"q":"شرکت هنر"})
    assert by_beneficiary.context["result_count"]>=2
    assert beneficiary.sama_code in by_beneficiary.content.decode()

    by_expert=client.get("/search/",{"q":"EXP-LIC-177"})
    assert expert.sama_code in by_expert.content.decode()


@pytest.mark.django_db
def test_global_search_empty_query_does_not_dump_data(client, dashboard_user):
    client.force_login(dashboard_user)
    CommercialSpace.objects.create(code="178",name="نباید بدون جست‌وجو دیده شود",status="ACTIVE")
    response=client.get("/search/")
    assert response.status_code==200
    assert response.context["result_count"]==0
    assert "نباید بدون جست‌وجو دیده شود" not in response.content.decode()
