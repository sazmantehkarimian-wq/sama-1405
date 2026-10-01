from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError

from domains.identity.models import AuditEvent
from domains.operations.models import (
    ElectricityAllocation,
    ElectricityBill,
    ElectricityCalculationSnapshot,
    ElectricityConsumptionCategory,
    UtilityMeasurement,
    UtilityUnit,
)
from domains.properties.models import CommercialSpace
from services.electricity import (
    create_electricity_bill,
    finalize_electricity_bill,
    record_measurement,
    recalculate_electricity_bill,
    reopen_electricity_bill,
    update_electricity_bill,
    upsert_electricity_allocation,
)


@pytest.fixture
def electricity_context(db):
    user=get_user_model().objects.create_user("power-user",password="A-very-safe-password")
    unit=UtilityUnit.objects.create(name="واحد آزمون",kind="OTHER",created_by=user)
    s1=CommercialSpace.objects.create(code="8101",name="فضای اول",status="ACTIVE",area=100)
    s2=CommercialSpace.objects.create(code="8102",name="فضای دوم",status="ACTIVE",area=100)
    return user,unit,s1,s2


@pytest.mark.django_db
def test_bill_requires_percent_total_exactly_100(electricity_context):
    user,unit,_,_=electricity_context
    with pytest.raises(ValidationError):
        create_electricity_bill(
            unit=unit,actor=user,
            values={
                "period_start":"1405/07/01","period_end":"1405/07/30",
                "amount_rial":"1000000","beneficiary_share_percent":"65",
                "organization_share_percent":"34",
            },
        )
    assert ElectricityBill.objects.count()==0


@pytest.mark.django_db
def test_measurement_has_priority_over_approved_model_and_amounts_balance(electricity_context):
    user,unit,s1,s2=electricity_context
    bill=create_electricity_bill(
        unit=unit,actor=user,
        values={
            "period_start":"1405/07/01","period_end":"1405/07/30",
            "amount_rial":"1000000","beneficiary_share_percent":"60",
            "organization_share_percent":"40",
        },
    )
    category=ElectricityConsumptionCategory.objects.create(name="فرهنگی",eui=Decimal("10"))
    measurement=record_measurement(
        space=s1,actor=user,
        values={
            "utility_type":"ELECTRICITY","period_start":"1405/07/01","period_end":"1405/07/30",
            "consumption":"300","reading_date":"1405/07/30","measurement_unit":"kWh",
            "is_submeter":True,"is_valid":True,
        },
    )
    upsert_electricity_allocation(
        bill=bill,space=s1,actor=user,
        values={"eligible":True,"measurement":measurement},
    )
    upsert_electricity_allocation(
        bill=bill,space=s2,actor=user,
        values={
            "eligible":True,"category":category,"effective_area":"100",
            "operational_factor":"1",
        },
    )
    bill.refresh_from_db()
    a1=ElectricityAllocation.objects.get(bill=bill,space=s1)
    a2=ElectricityAllocation.objects.get(bill=bill,space=s2)
    assert a1.calculation_source=="SUBMETER"
    assert a1.confidence_level=="REAL_MEASUREMENT"
    assert a2.calculation_source=="APPROVED_MODEL"
    assert a1.calculated_share_percent+a2.calculated_share_percent==Decimal("60.0000")
    assert bill.status=="CALCULATED"
    assert a1.payable_amount_rial+a2.payable_amount_rial+bill.organization_amount_rial==bill.amount_rial


@pytest.mark.django_db
def test_null_override_and_zero_override_are_distinct(electricity_context):
    user,unit,s1,s2=electricity_context
    user.is_staff=True;user.save(update_fields=["is_staff"])
    bill=create_electricity_bill(
        unit=unit,actor=user,
        values={
            "period_start":"1405/08/01","period_end":"1405/08/30",
            "amount_rial":"900000","beneficiary_share_percent":"60",
            "organization_share_percent":"40",
        },
    )
    upsert_electricity_allocation(
        bill=bill,space=s1,actor=user,
        values={"eligible":True,"effective_area":"100","eui":"10","operational_factor":"1"},
    )
    first=ElectricityAllocation.objects.get(bill=bill,space=s1)
    assert first.manual_override_percent is None

    upsert_electricity_allocation(
        bill=bill,space=s1,actor=user,
        values={
            "eligible":True,"effective_area":"100","eui":"10","operational_factor":"1",
            "manual_override_percent":"0","override_reason":"تصمیم معتبر سهم صفر",
        },
    )
    first.refresh_from_db();bill.refresh_from_db()
    assert first.manual_override_percent==Decimal("0")
    assert first.final_share_percent==Decimal("0")
    assert first.calculation_source=="MANUAL_OVERRIDE"
    assert bill.status=="REVIEW_REQUIRED"


@pytest.mark.django_db
def test_override_requires_reason(electricity_context):
    user,unit,s1,_=electricity_context
    user.is_staff=True;user.save(update_fields=["is_staff"])
    bill=create_electricity_bill(
        unit=unit,actor=user,
        values={
            "period_start":"1405/09/01","period_end":"1405/09/30",
            "amount_rial":"500000","beneficiary_share_percent":"50",
            "organization_share_percent":"50",
        },
    )
    with pytest.raises(ValidationError):
        upsert_electricity_allocation(
            bill=bill,space=s1,actor=user,
            values={
                "eligible":True,"effective_area":"100","eui":"10",
                "manual_override_percent":"50","override_reason":"",
            },
        )


@pytest.mark.django_db
def test_finalize_snapshot_is_immutable_and_final_bill_requires_reopen(electricity_context):
    user,unit,s1,_=electricity_context
    user.is_staff=True;user.save(update_fields=["is_staff"])
    bill=create_electricity_bill(
        unit=unit,actor=user,
        values={
            "period_start":"1405/10/01","period_end":"1405/10/30",
            "amount_rial":"1000000","beneficiary_share_percent":"70",
            "organization_share_percent":"30",
        },
    )
    upsert_electricity_allocation(
        bill=bill,space=s1,actor=user,
        values={"eligible":True,"effective_area":"100","eui":"10","operational_factor":"1"},
    )
    snapshot=finalize_electricity_bill(bill=bill,actor=user)
    bill.refresh_from_db()
    assert bill.status=="FINAL"
    assert snapshot.version==1
    original_payload=snapshot.payload
    assert original_payload["allocations"][0]["final_share_percent"]=="70.0000"

    with pytest.raises(ValidationError):
        upsert_electricity_allocation(
            bill=bill,space=s1,actor=user,
            values={"eligible":True,"effective_area":"200","eui":"10"},
        )
    snapshot.refresh_from_db()
    assert snapshot.payload==original_payload

    reopen_electricity_bill(bill=bill,actor=user,reason="اصلاح مستند پارامتر")
    bill.refresh_from_db()
    assert bill.status=="REOPENED"
    assert bill.reopen_reason=="اصلاح مستند پارامتر"
    assert ElectricityCalculationSnapshot.objects.filter(bill=bill).count()==1
    assert AuditEvent.objects.filter(action="ELECTRICITY_REOPEN",entity_id=str(bill.pk)).exists()


@pytest.mark.django_db
def test_non_staff_cannot_reopen_final_bill(electricity_context):
    user,unit,s1,_=electricity_context
    bill=create_electricity_bill(
        unit=unit,actor=user,
        values={
            "period_start":"1405/11/01","period_end":"1405/11/30",
            "amount_rial":"100000","beneficiary_share_percent":"50",
            "organization_share_percent":"50",
        },
    )
    upsert_electricity_allocation(
        bill=bill,space=s1,actor=user,
        values={"eligible":True,"effective_area":"10","eui":"1"},
    )
    finalize_electricity_bill(bill=bill,actor=user)
    with pytest.raises(PermissionDenied):
        reopen_electricity_bill(bill=bill,actor=user,reason="تلاش غیرمجاز")


@pytest.mark.django_db
def test_electricity_ui_flow_uses_structured_entities(client):
    user=get_user_model().objects.create_user("power-ui",password="A-very-safe-password",is_staff=True)
    client.force_login(user)
    space=CommercialSpace.objects.create(code="8199",name="فضای UI",status="ACTIVE")
    unit=UtilityUnit.objects.create(name="واحد UI",kind="OTHER",created_by=user)

    response=client.post("/utilities/electricity/bills/new/",{
        "unit":unit.pk,"period_start":"1405/07/01","period_end":"1405/07/30",
        "amount_rial":"1000000","beneficiary_share_percent":"100","organization_share_percent":"0",
    })
    assert response.status_code==302
    bill=ElectricityBill.objects.get()
    assert response.url.endswith(f"/utilities/electricity/bills/{bill.pk}/")

    response=client.post(f"/utilities/electricity/bills/{bill.pk}/allocations/",{
        "space":space.pk,"eligible":"on","effective_area":"100","eui":"10","operational_factor":"1",
    })
    assert response.status_code==302
    allocation=ElectricityAllocation.objects.get(bill=bill,space=space)
    assert allocation.final_share_percent==Decimal("100.0000")
    assert allocation.payable_amount_rial==Decimal("1000000")


@pytest.mark.django_db
def test_manual_share_override_requires_authorized_user(electricity_context):
    user,unit,s1,_=electricity_context
    bill=create_electricity_bill(
        unit=unit,actor=user,
        values={
            "period_start":"1405/12/01","period_end":"1405/12/29",
            "amount_rial":"100000","beneficiary_share_percent":"50",
            "organization_share_percent":"50",
        },
    )
    with pytest.raises(PermissionDenied):
        upsert_electricity_allocation(
            bill=bill,space=s1,actor=user,
            values={
                "eligible":True,"effective_area":"10","eui":"1",
                "manual_override_percent":"50","override_reason":"اصلاح مدیریتی",
            },
        )


@pytest.mark.django_db
def test_measurement_outside_bill_period_cannot_be_used(electricity_context):
    user,unit,s1,_=electricity_context
    bill=create_electricity_bill(
        unit=unit,actor=user,
        values={
            "period_start":"1405/07/01","period_end":"1405/07/30",
            "amount_rial":"100000","beneficiary_share_percent":"50",
            "organization_share_percent":"50",
        },
    )
    measurement=record_measurement(
        space=s1,actor=user,
        values={
            "utility_type":"ELECTRICITY","period_start":"1405/09/01","period_end":"1405/09/30",
            "consumption":"10","reading_date":"1405/09/30","is_valid":True,
        },
    )
    with pytest.raises(ValidationError):
        upsert_electricity_allocation(
            bill=bill,space=s1,actor=user,
            values={"eligible":True,"measurement":measurement},
        )


@pytest.mark.django_db
def test_bill_share_update_is_authorized_audited_and_recalculates(electricity_context):
    user,unit,s1,_=electricity_context
    user.is_staff=True;user.save(update_fields=["is_staff"])
    bill=create_electricity_bill(
        unit=unit,actor=user,
        values={
            "period_start":"1406/01/01","period_end":"1406/01/31",
            "amount_rial":"1000000","beneficiary_share_percent":"60",
            "organization_share_percent":"40",
        },
    )
    upsert_electricity_allocation(
        bill=bill,space=s1,actor=user,
        values={"eligible":True,"effective_area":"100","eui":"1"},
    )
    update_electricity_bill(
        bill=bill,actor=user,
        values={
            "amount_rial":"2000000",
            "beneficiary_share_percent":"70",
            "organization_share_percent":"30",
            "notes":"اصلاح مصوب",
        },
        reason="نامه اصلاح سهم",
    )
    bill.refresh_from_db()
    allocation=ElectricityAllocation.objects.get(bill=bill,space=s1)
    assert bill.amount_rial==Decimal("2000000")
    assert bill.beneficiary_share_percent==Decimal("70")
    assert allocation.final_share_percent==Decimal("70.0000")
    assert allocation.payable_amount_rial==Decimal("1400000")
    event=AuditEvent.objects.get(action="ELECTRICITY_BILL_UPDATE",entity_id=str(bill.pk))
    assert event.reason=="نامه اصلاح سهم"
    assert Decimal(event.before["beneficiary_share_percent"])==Decimal("60")
