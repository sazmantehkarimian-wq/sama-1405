from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model

from domains.properties.models import CommercialSpace, Region
from domains.utilities.models import (
    UtilityAccount,
    UtilityAllocation,
    UtilityAllocationPolicy,
    UtilityBill,
    UtilityMeterReading,
    UtilitySpaceProfile,
)
from domains.utilities.services import calculate_bill


@pytest.mark.django_db
def test_method3_distributes_beneficiary_pool_and_preserves_total():
    user = get_user_model().objects.create_user(username="utilitytester", password="StrongPassword!123")
    region = Region.objects.create(code="1", name="منطقه یک")
    account = UtilityAccount.objects.create(utility_type="ELECTRICITY", title="فرهنگسرای ملل", region=region, created_by=user)
    UtilityAllocationPolicy.objects.create(account=account, beneficiary_percent=Decimal("60"), organization_percent=Decimal("40"))
    s1 = CommercialSpace.objects.create(code="1", name="بوفه", status="ACTIVE", region=region, area=5, source_row=1, source_classification="ACTIVE")
    s2 = CommercialSpace.objects.create(code="3", name="فرهنگی", status="ACTIVE", region=region, area=308, source_row=2, source_classification="ACTIVE")
    UtilitySpaceProfile.objects.create(account=account, space=s1, eui=320, hours_factor=Decimal("1.520987654321"), manual_share_percent=Decimal("1"))
    UtilitySpaceProfile.objects.create(account=account, space=s2, eui=120, hours_factor=Decimal("2.196078431373"))
    bill = UtilityBill.objects.create(account=account, amount_rial=494_808_000, created_by=user)
    result = calculate_bill(bill)
    bill.refresh_from_db()
    assert result.organization_percent == Decimal("40")
    assert result.beneficiary_percent == Decimal("60")
    assert bill.organization_amount_rial + bill.beneficiary_amount_rial == bill.amount_rial
    assert bill.allocations.count() == 2
    manual = bill.allocations.get(profile__space=s1)
    assert manual.basis == UtilityAllocation.Basis.MANUAL
    assert manual.share_percent == Decimal("1.00000000")


@pytest.mark.django_db
def test_manual_locked_share_over_base_moves_excess_from_organization():
    user = get_user_model().objects.create_user(username="u2", password="StrongPassword!123")
    region = Region.objects.create(code="2", name="منطقه دو")
    account = UtilityAccount.objects.create(utility_type="ELECTRICITY", title="مرکز", region=region)
    UtilityAllocationPolicy.objects.create(account=account, beneficiary_percent=Decimal("20"), organization_percent=Decimal("80"))
    s1 = CommercialSpace.objects.create(code="10", name="فضا", status="ACTIVE", region=region, area=10, source_row=1, source_classification="ACTIVE")
    UtilitySpaceProfile.objects.create(account=account, space=s1, eui=1, manual_share_percent=Decimal("30"), manual_share_locked=True)
    bill = UtilityBill.objects.create(account=account, amount_rial=1_000_000)
    result = calculate_bill(bill)
    assert result.beneficiary_percent == Decimal("30")
    assert result.organization_percent == Decimal("70")
    assert result.beneficiary_amount_rial == Decimal("300000")
    assert result.organization_amount_rial == Decimal("700000")


@pytest.mark.django_db
def test_measured_reading_has_priority_over_method3_weight():
    region = Region.objects.create(code="3", name="منطقه سه")
    account = UtilityAccount.objects.create(utility_type="ELECTRICITY", title="مرکز", region=region)
    UtilityAllocationPolicy.objects.create(account=account, beneficiary_percent=100, organization_percent=0)
    s1 = CommercialSpace.objects.create(code="20", name="الف", status="ACTIVE", region=region, area=1000, source_row=1, source_classification="ACTIVE")
    s2 = CommercialSpace.objects.create(code="21", name="ب", status="ACTIVE", region=region, area=1, source_row=2, source_classification="ACTIVE")
    p1 = UtilitySpaceProfile.objects.create(account=account, space=s1, eui=999)
    UtilitySpaceProfile.objects.create(account=account, space=s2, eui=1)
    bill = UtilityBill.objects.create(account=account, amount_rial=1000)
    UtilityMeterReading.objects.create(bill=bill, profile=p1, measured_consumption=1, is_valid=True)
    calculate_bill(bill)
    a1 = bill.allocations.get(profile=p1)
    assert a1.basis == UtilityAllocation.Basis.MEASURED
    assert a1.consumption_weight == Decimal("1")
