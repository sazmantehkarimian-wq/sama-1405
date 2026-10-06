import pytest
from django.contrib.auth import get_user_model

from domains.masterdata.models import OrganizationPerson, OrganizationUnit, PositionAssignment
from domains.properties.models import Center, CommercialSpace, MotherProperty, Region

pytestmark = pytest.mark.django_db


def login(client):
    user = get_user_model().objects.create_user("masterdata-user")
    client.force_login(user)
    return user


def seed_property_data():
    region = Region.objects.create(code="1", name="منطقه یک")
    center = Center.objects.create(name="مرکز نمونه", region=region, is_special=True)
    mother = MotherProperty.objects.create(identifier="P-1", name="ملک مادر نمونه", region=region, primary_usage="فرهنگی", center_type="فرهنگسرا", source_row=2)
    active = CommercialSpace.objects.create(code="173", name="فضای فعال", status=CommercialSpace.Status.ACTIVE, region=region, center=center, current_usage="کافی‌شاپ", proposed_activity="پذیرایی", activity_group="خوراک", source_row=3, source_classification="authority")
    inactive = CommercialSpace.objects.create(code="174", name="فضای خارج از چرخه", status=CommercialSpace.Status.OUT_OF_CYCLE, region=region, center=center, previous_usage="فروشگاهی", source_row=4, source_classification="authority")
    return region, center, mother, active, inactive


def test_masterdata_requires_login(client):
    response = client.get("/master-data/")
    assert response.status_code == 302
    assert "/login/" in response.url


def test_dashboard_and_combined_search(client):
    login(client)
    region, center, mother, active, inactive = seed_property_data()
    dashboard = client.get("/master-data/")
    assert dashboard.status_code == 200
    body = dashboard.content.decode()
    assert "اطلاعات پایه و املاک" in body
    assert "۲" in body or "2" in body

    response = client.get("/master-data/search/", {"region": region.id, "center": center.id, "status": "ACTIVE", "activity": "پذیرایی", "special": "1"})
    body = response.content.decode()
    assert response.status_code == 200
    assert "173" in body
    assert "174" not in body


def test_people_are_editable_and_old_assignment_is_preserved(client):
    login(client)
    unit = OrganizationUnit.objects.create(code="REALESTATE", name="اداره املاک و مستغلات", unit_type=OrganizationUnit.UnitType.DEPARTMENT)
    old_person = OrganizationPerson.objects.create(full_name="مدیر قبلی")
    old_assignment = PositionAssignment.objects.create(person=old_person, unit=unit, title="رئیس اداره", start_date="1404/01/01", is_current=True)
    new_person = OrganizationPerson.objects.create(full_name="مدیر جدید")

    response = client.post("/master-data/organization/assignments/add/", {"person": new_person.id, "unit": unit.id, "title": "رئیس اداره", "start_date": "1405/07/15", "end_date": "", "is_current": "on", "notes": ""})
    assert response.status_code == 302
    old_assignment.refresh_from_db()
    assert old_assignment.is_current is False
    assert PositionAssignment.objects.filter(person=old_person, title="رئیس اداره").exists()
    assert PositionAssignment.objects.get(person=new_person, title="رئیس اداره").is_current is True

    response = client.post(f"/master-data/organization/people/{new_person.id}/edit/", {"full_name": "مدیر جدید ویرایش‌شده", "mobile": "09120000000", "phone": "", "extension": "123", "email": "", "notes": "", "is_active": "on"})
    assert response.status_code == 302
    new_person.refresh_from_db()
    assert new_person.full_name == "مدیر جدید ویرایش‌شده"
    assert new_person.extension == "123"


def test_person_can_hold_multiple_current_roles(client):
    login(client)
    person = OrganizationPerson.objects.create(full_name="مسئول مشترک")
    unit_a = OrganizationUnit.objects.create(code="A", name="واحد الف", unit_type=OrganizationUnit.UnitType.MANAGEMENT)
    unit_b = OrganizationUnit.objects.create(code="B", name="واحد ب", unit_type=OrganizationUnit.UnitType.DEPARTMENT)
    PositionAssignment.objects.create(person=person, unit=unit_a, title="مدیر", is_current=True)

    response = client.post("/master-data/organization/assignments/add/", {"person": person.id, "unit": unit_b.id, "title": "سرپرست", "start_date": "1405/07/15", "end_date": "", "is_current": "on", "notes": ""})
    assert response.status_code == 302
    assert PositionAssignment.objects.filter(person=person, is_current=True).count() == 2
