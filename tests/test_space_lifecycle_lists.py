import datetime

import jdatetime
import pytest
from django.contrib.auth import get_user_model

from domains.contracts.models import Beneficiary, BeneficiaryAssignment, Contract
from domains.properties.models import CommercialSpace


def jdate(delta_days=0):
    today = jdatetime.date.today().togregorian()
    target = today + datetime.timedelta(days=delta_days)
    return jdatetime.date.fromgregorian(date=target).strftime("%Y/%m/%d")


@pytest.mark.django_db
def test_active_and_out_of_cycle_lists_are_separate_and_show_correct_contract_context(client):
    user = get_user_model().objects.create_user("lifecycle-user", password="A-very-safe-password")
    client.force_login(user)

    active = CommercialSpace.objects.create(code="7101", name="فضای فعال", status="ACTIVE")
    inactive = CommercialSpace.objects.create(code="7102", name="فضای خارج از چرخه", status="OUT_OF_CYCLE")
    current_beneficiary = Beneficiary.objects.create(kind="NATURAL", name="بهره‌بردار جاری", first_name="بهره‌بردار", last_name="جاری")
    old_beneficiary = Beneficiary.objects.create(kind="LEGAL", name="شرکت قبلی", legal_name="شرکت قبلی")

    Contract.objects.create(
        space=active, beneficiary=current_beneficiary, number="CUR-1",
        start_date=jdate(-10), end_date=jdate(30),
    )
    BeneficiaryAssignment.objects.create(
        space=active, beneficiary=current_beneficiary, role="بهره‌بردار",
        start_date=jdate(-10), end_date="", status="ACTIVE",
    )
    Contract.objects.create(
        space=inactive, beneficiary=old_beneficiary, number="OLD-1",
        start_date=jdate(-400), end_date=jdate(-20),
    )
    BeneficiaryAssignment.objects.create(
        space=inactive, beneficiary=old_beneficiary, role="بهره‌بردار",
        start_date=jdate(-400), end_date=jdate(-20), status="ENDED",
    )

    active_response = client.get("/spaces/active/")
    active_body = active_response.content.decode()
    assert active_response.status_code == 200
    assert "7101" in active_body and "7102" not in active_body
    assert "بهره‌بردار جاری" in active_body and "CUR-1" in active_body

    inactive_response = client.get("/spaces/out-of-cycle/")
    inactive_body = inactive_response.content.decode()
    assert inactive_response.status_code == 200
    assert "7102" in inactive_body and "7101" not in inactive_body
    assert "شرکت قبلی" in inactive_body and "OLD-1" in inactive_body


@pytest.mark.django_db
def test_scope_search_points_user_to_correct_space_group(client):
    user = get_user_model().objects.create_user("scope-user", password="A-very-safe-password")
    client.force_login(user)
    CommercialSpace.objects.create(code="7201", name="فضای خارج", status="OUT_OF_CYCLE")

    response = client.get("/spaces/active/", {"code": "7201"})
    body = response.content.decode()
    assert response.status_code == 200
    assert "در این گروه نیست" in body
    assert "/spaces/out-of-cycle/?code=7201" in body


@pytest.mark.django_db
def test_contract_temporal_status_and_duration_are_derived_not_entered():
    space = CommercialSpace.objects.create(code="7301", name="فضا", status="ACTIVE")
    beneficiary = Beneficiary.objects.create(kind="LEGAL", name="شرکت آزمون", legal_name="شرکت آزمون")

    current = Contract.objects.create(
        space=space, beneficiary=beneficiary, number="T-CURRENT",
        start_date=jdate(-5), end_date=jdate(20),
    )
    future = Contract.objects.create(
        space=space, beneficiary=beneficiary, number="T-FUTURE",
        start_date=jdate(40), end_date=jdate(80),
    )
    ended = Contract.objects.create(
        space=space, beneficiary=beneficiary, number="T-ENDED",
        start_date=jdate(-80), end_date=jdate(-40),
    )

    assert current.time_status == "CURRENT"
    assert future.time_status == "NOT_STARTED"
    assert ended.time_status == "ENDED"
    assert current.remaining_days == 20
    assert current.duration_days == 26
