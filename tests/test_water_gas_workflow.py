import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from domains.identity.models import AuditEvent
from domains.operations.models import ElectricityAllocation, UtilityBill, UtilityConnection, UtilityMeasurement
from domains.properties.models import CommercialSpace
from services.electricity import record_measurement
from services.utilities import create_utility_bill, create_utility_connection


@pytest.mark.django_db
def test_water_and_gas_connections_are_independent_from_electricity():
    user=get_user_model().objects.create_user("utility-user",password="A-very-safe-password")
    space=CommercialSpace.objects.create(code="8301",name="فضای انشعاب",status="ACTIVE")
    water=create_utility_connection(
        space=space,actor=user,
        values={"utility_type":"WATER","account_number":"W-100","meter_number":"WM-1"},
    )
    gas=create_utility_connection(
        space=space,actor=user,
        values={"utility_type":"GAS","account_number":"G-100","meter_number":"GM-1"},
    )
    assert water.utility_type=="WATER" and gas.utility_type=="GAS"
    assert ElectricityAllocation.objects.count()==0
    assert AuditEvent.objects.filter(action="UTILITY_CONNECTION_CREATE").count()==2


@pytest.mark.django_db
def test_water_bill_accepts_matching_measurement_without_electricity_formula():
    user=get_user_model().objects.create_user("water-user",password="A-very-safe-password")
    space=CommercialSpace.objects.create(code="8302",name="فضای آب",status="ACTIVE")
    connection=create_utility_connection(
        space=space,actor=user,
        values={"utility_type":"WATER","account_number":"W-200"},
    )
    measurement=record_measurement(
        space=space,actor=user,
        values={
            "utility_type":"WATER","period_start":"1405/07/01","period_end":"1405/07/30",
            "consumption":"12.500","reading_date":"1405/07/30","measurement_unit":"m3","is_valid":True,
        },
    )
    bill=create_utility_bill(
        connection=connection,actor=user,
        values={
            "period_start":"1405/07/01","period_end":"1405/07/30",
            "amount_rial":"750000","consumption":"12.500","measurement":measurement,
            "payment_status":"UNPAID",
        },
    )
    assert bill.measurement==measurement
    assert bill.consumption==measurement.consumption
    assert bill.sama_code.startswith("UTB-")
    assert ElectricityAllocation.objects.count()==0


@pytest.mark.django_db
def test_utility_bill_rejects_measurement_from_other_type_or_period():
    user=get_user_model().objects.create_user("utility-validation",password="A-very-safe-password")
    space=CommercialSpace.objects.create(code="8303",name="فضا",status="ACTIVE")
    connection=create_utility_connection(
        space=space,actor=user,
        values={"utility_type":"GAS","account_number":"G-300"},
    )
    water_measurement=UtilityMeasurement.objects.create(
        space=space,utility_type="WATER",period_start="1405/07/01",period_end="1405/07/30",
        consumption="5",reading_date="1405/07/30",measurement_unit="m3",is_valid=True,created_by=user,
    )
    with pytest.raises(ValidationError):
        create_utility_bill(
            connection=connection,actor=user,
            values={
                "period_start":"1405/07/01","period_end":"1405/07/30",
                "amount_rial":"100000","measurement":water_measurement,
                "payment_status":"UNKNOWN",
            },
        )


@pytest.mark.django_db
def test_paid_utility_bill_requires_payment_date():
    user=get_user_model().objects.create_user("paid-utility",password="A-very-safe-password")
    space=CommercialSpace.objects.create(code="8304",name="فضا",status="ACTIVE")
    connection=create_utility_connection(
        space=space,actor=user,
        values={"utility_type":"WATER","account_number":"W-400"},
    )
    with pytest.raises(ValidationError):
        create_utility_bill(
            connection=connection,actor=user,
            values={
                "period_start":"1405/08/01","period_end":"1405/08/30",
                "amount_rial":"100000","payment_status":"PAID","payment_date":"",
            },
        )


@pytest.mark.django_db
def test_water_gas_ui_flow(client):
    user=get_user_model().objects.create_user("utility-ui",password="A-very-safe-password")
    client.force_login(user)
    space=CommercialSpace.objects.create(code="8399",name="فضای UI",status="ACTIVE")
    response=client.post("/spaces/8399/utility-connections/new/",{
        "utility_type":"WATER","account_number":"W-UI","meter_number":"M-UI","status":"ACTIVE",
    })
    assert response.status_code==302
    connection=UtilityConnection.objects.get()
    response=client.post(f"/utility-connections/{connection.pk}/bills/new/",{
        "period_start":"1405/07/01","period_end":"1405/07/30",
        "amount_rial":"200000","consumption":"4.5","payment_status":"UNPAID",
    })
    assert response.status_code==302
    assert UtilityBill.objects.filter(connection=connection).exists()
    body=client.get("/spaces/8399/").content.decode()
    assert "W-UI" in body
    assert "UTB-" in body
