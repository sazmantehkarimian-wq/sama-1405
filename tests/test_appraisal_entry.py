import pytest
from django.contrib.auth import get_user_model

from domains.identity.models import AuditEvent
from domains.operations.models import Appraiser, Appraisal, AppraisalNotification
from domains.properties.models import CommercialSpace


@pytest.mark.django_db
def test_appraiser_entry_duplicate_controls_and_audit(client):
    user=get_user_model().objects.create_user("appraiser-user",password="A-very-safe-password")
    client.force_login(user)
    payload={
        "first_name":"نوید","last_name":"دولت‌آبادی","national_id":"1234567890",
        "license_number":"LIC-100","specialty":"ارزیابی املاک","collaboration_status":"ACTIVE",
    }
    response=client.post("/appraisers/new/",payload)
    assert response.status_code==302
    appraiser=Appraiser.objects.get()
    assert appraiser.sama_code.startswith("EXP-")
    assert AuditEvent.objects.filter(action="APPRAISER_CREATE",entity_id=str(appraiser.pk)).exists()

    duplicate=client.post("/appraisers/new/",dict(payload,first_name="کارشناس",last_name="تکراری"))
    assert duplicate.status_code==200
    assert Appraiser.objects.count()==1
    assert "کارشناس دیگری با این کد ملی ثبت شده است" in duplicate.content.decode()


@pytest.mark.django_db
def test_appraisal_dates_are_independent_and_notification_is_structured(client):
    user=get_user_model().objects.create_user("appraisal-user",password="A-very-safe-password")
    client.force_login(user)
    space=CommercialSpace.objects.create(code="6201",name="فضای کارشناسی",status="ACTIVE")
    appraiser=Appraiser.objects.create(first_name="علی",last_name="کارشناس",created_by=user)

    response=client.post("/spaces/6201/appraisals/new/",{
        "appraiser":appraiser.pk,
        "notification_number":"N-1",
        "notification_date":"1405/07/01",
        "notification_recipient":"EXPERT",
        "response_number":"R-1",
        "response_date":"1405/07/05",
        "appraisal_date":"1405/07/03",
        "amount_rial":"2500000",
        "status":"تکمیل‌شده",
        "is_current":"on",
    })
    assert response.status_code==302
    appraisal=Appraisal.objects.get()
    assert appraisal.appraiser_ref==appraiser
    assert appraisal.response_date=="1405/07/05"
    assert appraisal.appraisal_date=="1405/07/03"
    assert appraisal.is_current is True
    notification=AppraisalNotification.objects.get(appraisal=appraisal)
    assert notification.notification_date=="1405/07/01"
    assert notification.recipient=="EXPERT"
    assert AuditEvent.objects.filter(action="APPRAISAL_CREATE",entity_id=str(appraisal.pk)).exists()


@pytest.mark.django_db
def test_only_one_current_appraisal_per_space_via_service_ui(client):
    user=get_user_model().objects.create_user("appraisal-current",password="A-very-safe-password")
    client.force_login(user)
    space=CommercialSpace.objects.create(code="6202",name="فضا",status="ACTIVE")
    appraiser=Appraiser.objects.create(first_name="مریم",last_name="کارشناس",created_by=user)

    first={"appraiser":appraiser.pk,"appraisal_date":"1405/06/01","amount_rial":"1000000","is_current":"on"}
    second={"appraiser":appraiser.pk,"appraisal_date":"1405/07/01","amount_rial":"1200000","is_current":"on"}
    assert client.post("/spaces/6202/appraisals/new/",first).status_code==302
    old=Appraisal.objects.get()
    assert old.is_current
    assert client.post("/spaces/6202/appraisals/new/",second).status_code==302
    old.refresh_from_db()
    assert old.is_current is False
    assert Appraisal.objects.filter(space=space,is_current=True).count()==1


@pytest.mark.django_db
def test_current_appraisal_requires_date_and_amount(client):
    user=get_user_model().objects.create_user("appraisal-validation",password="A-very-safe-password")
    client.force_login(user)
    CommercialSpace.objects.create(code="6203",name="فضا",status="ACTIVE")
    appraiser=Appraiser.objects.create(first_name="رضا",last_name="کارشناس")
    response=client.post("/spaces/6203/appraisals/new/",{
        "appraiser":appraiser.pk,
        "is_current":"on",
    })
    assert response.status_code==200
    assert Appraisal.objects.count()==0
    assert "کارشناسی مرجع باید تاریخ خود کارشناسی و مبلغ کارشناسی داشته باشد" in response.content.decode()
