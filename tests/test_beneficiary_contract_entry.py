import pytest
from django.contrib.auth import get_user_model

from domains.contracts.models import Beneficiary, Contract
from domains.identity.models import AuditEvent
from domains.properties.models import CommercialSpace


@pytest.mark.django_db
def test_beneficiary_manual_entry_supports_partial_identity_and_duplicate_control(client):
    user = get_user_model().objects.create_user("beneficiary-user", password="A-very-safe-password")
    client.force_login(user)

    response = client.post("/beneficiaries/new/", {
        "kind": "NATURAL",
        "first_name": "علی",
        "last_name": "نمونه",
        "identity_number": "",
        "mobile": "09121234567",
    })
    assert response.status_code == 302
    beneficiary = Beneficiary.objects.get()
    assert beneficiary.name == "علی نمونه"
    assert beneficiary.completeness_status == "نیازمند تکمیل هویت"
    assert AuditEvent.objects.filter(action="BENEFICIARY_CREATE", entity_id=str(beneficiary.pk)).exists()

    second = client.post("/beneficiaries/new/", {
        "kind": "LEGAL",
        "legal_name": "شرکت نمونه",
        "identity_number": "12345678901",
    })
    assert second.status_code == 302
    duplicate = client.post("/beneficiaries/new/", {
        "kind": "LEGAL",
        "legal_name": "شرکت دوم",
        "identity_number": "12345678901",
    })
    assert duplicate.status_code == 200
    assert Beneficiary.objects.count() == 2
    assert "پرونده‌ای با این شناسه قبلاً ثبت شده است" in duplicate.content.decode()


@pytest.mark.django_db
def test_contract_entry_requires_existing_beneficiary_and_blocks_overlap(client):
    user = get_user_model().objects.create_user("contract-user", password="A-very-safe-password")
    client.force_login(user)
    space = CommercialSpace.objects.create(code="6101", name="فضای قرارداد", status="ACTIVE")
    beneficiary = Beneficiary.objects.create(
        kind="NATURAL", name="مریم نمونه", first_name="مریم", last_name="نمونه", created_by=user
    )

    payload = {
        "beneficiary": beneficiary.pk,
        "number": "C-1",
        "signed_date": "1405/07/01",
        "start_date": "1405/07/01",
        "end_date": "1405/12/29",
        "amount_rial": "1000000",
    }
    response = client.post("/spaces/6101/contracts/new/", payload)
    assert response.status_code == 302
    first = Contract.objects.get(number="C-1")
    assert first.beneficiary == beneficiary
    assert Beneficiary.objects.count() == 1

    overlap = dict(payload, number="C-2", start_date="1405/10/01", end_date="1406/01/31")
    response = client.post("/spaces/6101/contracts/new/", overlap)
    assert response.status_code == 200
    assert Contract.objects.count() == 1
    assert "دارای قرارداد دیگری است" in response.content.decode()

    consecutive = dict(payload, number="C-3", start_date="1406/01/01", end_date="1406/12/29")
    response = client.post("/spaces/6101/contracts/new/", consecutive)
    assert response.status_code == 302
    assert Contract.objects.filter(number="C-3").exists()


@pytest.mark.django_db
def test_contract_more_than_365_days_is_long_term():
    space = CommercialSpace.objects.create(code="6102", name="فضای بلندمدت", status="ACTIVE")
    beneficiary = Beneficiary.objects.create(kind="LEGAL", name="شرکت الف", legal_name="شرکت الف")
    contract = Contract.objects.create(
        space=space,
        beneficiary=beneficiary,
        number="LONG-1",
        start_date="1405/01/01",
        end_date="1406/01/02",
    )
    assert contract.duration_days > 365
    assert contract.is_long_term is True


@pytest.mark.django_db
def test_beneficiary_detail_keeps_space_and_contract_links(client):
    user = get_user_model().objects.create_user("beneficiary-view", password="A-very-safe-password")
    client.force_login(user)
    beneficiary = Beneficiary.objects.create(kind="NATURAL", name="حسن نمونه", first_name="حسن", last_name="نمونه")
    response = client.get(f"/beneficiaries/{beneficiary.pk}/")
    assert response.status_code == 200
    body = response.content.decode()
    assert beneficiary.sama_code in body
    assert "فضاهای جاری و سابقه ارتباط" in body
    assert "قراردادها" in body
