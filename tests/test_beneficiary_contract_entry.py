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


@pytest.mark.django_db
def test_beneficiary_and_contract_search_use_identity_fields(client):
    user=get_user_model().objects.create_user("search-contracts",password="A-very-safe-password")
    client.force_login(user)
    space=CommercialSpace.objects.create(code="6109",name="فضای جست‌وجو",status="ACTIVE")
    beneficiary=Beneficiary.objects.create(kind="LEGAL",name="شرکت جست‌وجو",legal_name="شرکت جست‌وجو",identity_number="12345678902")
    Contract.objects.create(space=space,beneficiary=beneficiary,number="CNT-SEARCH",start_date="1405/01/01",end_date="1405/12/29")

    by_code=client.get("/records/beneficiaries/",{"q":beneficiary.sama_code})
    assert "شرکت جست‌وجو" in by_code.content.decode()

    by_identity=client.get("/records/contracts/",{"q":"12345678902"})
    assert "CNT-SEARCH" in by_identity.content.decode()


@pytest.mark.django_db
def test_beneficiary_can_be_assigned_without_contract_and_list_shows_it(client):
    user=get_user_model().objects.create_user("beneficiary-assign",password="A-very-safe-password")
    client.force_login(user)
    space=CommercialSpace.objects.create(code="6110",name="فضای بدون قرارداد",status="ACTIVE")
    beneficiary=Beneficiary.objects.create(kind="NATURAL",name="ندا نمونه",first_name="ندا",last_name="نمونه")

    response=client.post("/spaces/6110/beneficiaries/assign/",{
        "beneficiary":beneficiary.pk,
        "start_date":"1405/07/01",
        "basis":"بهره‌برداری جاری",
    })
    assert response.status_code==302
    assignment=beneficiary.space_assignments.get(space=space)
    assert assignment.status=="ACTIVE" and assignment.end_date==""
    assert Contract.objects.filter(space=space).count()==0
    assert AuditEvent.objects.filter(action="BENEFICIARY_ASSIGNMENT_CREATE",entity_id=str(assignment.pk)).exists()

    listed=client.get("/spaces/active/")
    body=listed.content.decode()
    assert "ندا نمونه" in body
    assert "فاقد قرارداد" in body


@pytest.mark.django_db
def test_beneficiary_change_closes_previous_link_and_requires_reason(client):
    user=get_user_model().objects.create_user("beneficiary-change",password="A-very-safe-password")
    client.force_login(user)
    space=CommercialSpace.objects.create(code="6111",name="فضا",status="ACTIVE")
    first=Beneficiary.objects.create(kind="NATURAL",name="بهره‌بردار اول",first_name="بهره‌بردار",last_name="اول")
    second=Beneficiary.objects.create(kind="LEGAL",name="شرکت دوم",legal_name="شرکت دوم")

    assert client.post("/spaces/6111/beneficiaries/assign/",{
        "beneficiary":first.pk,"start_date":"1405/07/01","basis":"ثبت اولیه",
    }).status_code==302

    rejected=client.post("/spaces/6111/beneficiaries/assign/",{
        "beneficiary":second.pk,"start_date":"1405/08/01","basis":"تغییر بهره‌بردار",
    })
    assert rejected.status_code==200
    assert first.space_assignments.get(space=space).status=="ACTIVE"
    assert second.space_assignments.filter(space=space).count()==0

    accepted=client.post("/spaces/6111/beneficiaries/assign/",{
        "beneficiary":second.pk,"start_date":"1405/08/01","basis":"تغییر بهره‌بردار",
        "termination_reason":"ابلاغ تغییر بهره‌بردار",
    })
    assert accepted.status_code==302
    old=first.space_assignments.get(space=space)
    new=second.space_assignments.get(space=space)
    assert old.status=="ENDED" and old.end_date=="1405/07/31"
    assert old.termination_reason=="ابلاغ تغییر بهره‌بردار"
    assert new.status=="ACTIVE" and new.start_date=="1405/08/01"


@pytest.mark.django_db
def test_contract_does_not_duplicate_matching_beneficiary_assignment_and_rejects_mismatch(client):
    user=get_user_model().objects.create_user("contract-beneficiary-consistency",password="A-very-safe-password")
    client.force_login(user)
    space=CommercialSpace.objects.create(code="6112",name="فضا",status="ACTIVE")
    first=Beneficiary.objects.create(kind="NATURAL",name="بهره‌بردار اول",first_name="بهره‌بردار",last_name="اول")
    second=Beneficiary.objects.create(kind="LEGAL",name="شرکت دوم",legal_name="شرکت دوم")

    assert client.post("/spaces/6112/beneficiaries/assign/",{
        "beneficiary":first.pk,"start_date":"1405/07/01","basis":"بهره‌برداری جاری",
    }).status_code==302

    response=client.post("/spaces/6112/contracts/new/",{
        "beneficiary":first.pk,"number":"C-MATCH","start_date":"1405/08/01","end_date":"1405/12/29",
    })
    assert response.status_code==302
    assert first.space_assignments.filter(space=space).count()==1

    mismatch=client.post("/spaces/6112/contracts/new/",{
        "beneficiary":second.pk,"number":"C-MISMATCH","start_date":"1406/01/01","end_date":"1406/12/29",
    })
    assert mismatch.status_code==200
    assert not Contract.objects.filter(number="C-MISMATCH").exists()
    assert "ابتدا تغییر بهره‌بردار" in mismatch.content.decode()
