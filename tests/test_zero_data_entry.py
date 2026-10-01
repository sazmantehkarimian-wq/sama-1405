import importlib.util

import pytest
from django.contrib.auth import get_user_model
from django.db import DatabaseError

from domains.identity.models import AuditEvent
from domains.properties.models import CommercialSpace, MotherProperty
from ui.entry_forms import CommercialSpaceForm
from ui.fields import JalaliDateField


@pytest.mark.django_db
def test_zero_data_operational_tables_start_empty():
    assert CommercialSpace.objects.count() == 0
    assert MotherProperty.objects.count() == 0
    assert AuditEvent.objects.count() == 0


def test_excel_import_runtime_is_absent():
    assert importlib.util.find_spec("import_pipeline") is None


@pytest.mark.django_db
def test_space_code_is_numeric_unique_and_immutable_even_through_queryset_update():
    form = CommercialSpaceForm(data={"code": "173", "name": "فضای ۱۷۳", "status": "ACTIVE"})
    assert form.is_valid(), form.errors
    space = form.save()
    duplicate = CommercialSpaceForm(data={"code": "173", "name": "تکراری", "status": "ACTIVE"})
    assert not duplicate.is_valid()
    invalid = CommercialSpaceForm(data={"code": "0173", "name": "نامعتبر", "status": "ACTIVE"})
    assert not invalid.is_valid()
    with pytest.raises(DatabaseError):
        CommercialSpace.objects.filter(pk=space.pk).update(code="174")


@pytest.mark.django_db
def test_mother_property_is_independent_and_identifier_is_immutable():
    mother = MotherProperty.objects.create(identifier="P-0001", name="ملک مادر")
    assert not hasattr(mother, "space_links")
    with pytest.raises(DatabaseError):
        MotherProperty.objects.filter(pk=mother.pk).update(identifier="P-0002")


def test_jalali_date_field_accepts_only_real_dates():
    field = JalaliDateField()
    assert field.clean("۱۴۰۵/۰۷/۰۱") == "1405/07/01"
    for value in ("1405/13/01", "1405/02/32", "امروز", "1405-07-01"):
        with pytest.raises(Exception):
            field.clean(value)


@pytest.mark.django_db
def test_manual_space_creation_is_audited(client):
    user = get_user_model().objects.create_user("manual-entry", password="A-very-safe-password")
    client.force_login(user)
    response = client.post("/spaces/new/", {"code": "501", "name": "فضای ثبت دستی", "status": "ACTIVE"})
    assert response.status_code == 302
    assert CommercialSpace.objects.filter(code="501").exists()
    assert AuditEvent.objects.filter(
        action="COMMERCIAL_SPACE_CREATE", entity_type="CommercialSpace", entity_id="501"
    ).exists()
