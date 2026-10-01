import pytest
from django.contrib.auth import get_user_model

from domains.identity.models import AuditEvent
from domains.operations.models import FileMovement, TimelineEvent
from domains.properties.models import CommercialSpace
from services.file_movement import current_holder


@pytest.mark.django_db
def test_second_file_handover_is_blocked_until_current_holder_returns_file(client):
    user=get_user_model().objects.create_user("file-holder-user",password="A-very-safe-password")
    client.force_login(user)
    space=CommercialSpace.objects.create(code="8201",name="فضای پرونده",status="ACTIVE")

    first=client.post("/spaces/8201/movement/",{
        "location":"اداره املاک","holder":"کارشناس الف","delivered_by":"بایگانی","received_by":"کارشناس الف",
        "signature_state":"تحویل با امضا","direction":"OUT","next_action":"بررسی قرارداد","due_date":"1405/07/20",
    })
    assert first.status_code==302
    first_record=FileMovement.objects.get(space=space)
    assert first_record.returned_at is None
    assert current_holder(space).holder=="کارشناس الف"

    second=client.post("/spaces/8201/movement/",{
        "location":"مدیریت اقتصادی","holder":"مدیر ب","delivered_by":"کارشناس الف","received_by":"مدیر ب",
        "signature_state":"تحویل با امضا","direction":"OUT","next_action":"امضا","due_date":"1405/07/25",
    })
    assert second.status_code==302
    first_record.refresh_from_db()
    assert first_record.returned_at is None
    assert FileMovement.objects.filter(space=space,returned_at__isnull=True).count()==1
    assert current_holder(space).holder=="کارشناس الف"
    assert AuditEvent.objects.filter(action="FILE_MOVEMENT_CREATE",entity_id=space.code).count()==1

    assert client.post("/spaces/8201/movement/return/",{"reason":"تحویل به مدیر"}).status_code==302
    third=client.post("/spaces/8201/movement/",{
        "location":"مدیریت اقتصادی","holder":"مدیر ب","delivered_by":"کارشناس الف","received_by":"مدیر ب",
        "signature_state":"تحویل با امضا","direction":"OUT","next_action":"امضا","due_date":"1405/07/25",
    })
    assert third.status_code==302
    holder=current_holder(space)
    assert holder.holder=="مدیر ب" and holder.location=="مدیریت اقتصادی"
    assert holder.duration_days==0
    assert AuditEvent.objects.filter(action="FILE_MOVEMENT_CREATE",entity_id=space.code).count()==2
    assert TimelineEvent.objects.filter(space=space,event_type="FILE_MOVEMENT_CREATE").count()==2


@pytest.mark.django_db
def test_explicit_file_return_closes_current_holder_and_is_audited(client):
    user=get_user_model().objects.create_user("file-return-user",password="A-very-safe-password")
    client.force_login(user)
    space=CommercialSpace.objects.create(code="8202",name="فضا",status="ACTIVE")
    client.post("/spaces/8202/movement/",{
        "location":"دفتر مدیر","holder":"مدیر","delivered_by":"کارشناس","received_by":"مدیر",
        "signature_state":"امضا شد","direction":"OUT",
    })

    response=client.post("/spaces/8202/movement/return/",{"reason":"پرونده پس از امضا به بایگانی برگشت"})
    assert response.status_code==302
    movement=FileMovement.objects.get(space=space)
    assert movement.returned_at is not None
    assert current_holder(space) is None
    audit=AuditEvent.objects.get(action="FILE_MOVEMENT_RETURN",entity_id=space.code)
    assert audit.reason=="پرونده پس از امضا به بایگانی برگشت"
    assert TimelineEvent.objects.filter(space=space,event_type="FILE_MOVEMENT_RETURN").exists()


@pytest.mark.django_db
def test_file_handover_rejects_invalid_direction(client):
    user=get_user_model().objects.create_user("file-invalid-user",password="A-very-safe-password")
    client.force_login(user)
    space=CommercialSpace.objects.create(code="8203",name="فضا",status="ACTIVE")
    response=client.post("/spaces/8203/movement/",{
        "location":"محل","holder":"دارنده","delivered_by":"الف","received_by":"ب",
        "signature_state":"ثبت شد","direction":"UNKNOWN",
    })
    assert response.status_code==302
    assert FileMovement.objects.filter(space=space).count()==0
