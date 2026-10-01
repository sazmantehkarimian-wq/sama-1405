from decimal import Decimal

import jdatetime
import pytest
from django.contrib.auth import get_user_model

from domains.contracts.models import Beneficiary, Contract
from domains.operations.models import Appraisal, AuctionInstruction, AuctionRule
from domains.properties.models import CommercialSpace
from services.auctions import evaluate_space


@pytest.fixture
def auction_context(db):
    user = get_user_model().objects.create_user("auction-owner", password="A-very-safe-password")
    beneficiary = Beneficiary.objects.create(kind="LEGAL", name="شرکت آزمون", legal_name="شرکت آزمون")
    rule = AuctionRule.objects.create(version="1405.1", effective_year=1405,
        contract_window_min_days=1, contract_window_max_days=90,
        minor_ceiling_rial=Decimal("350000000"), medium_ceiling_rial=Decimal("3500000000"),
        appraisal_valid_months=6, active=True, change_reason="مرز مصوب مرجع ۱۴۰۵", approved_by=user)
    return user, beneficiary, rule


def _space(code):
    return CommercialSpace.objects.create(code=code, name="فضا", status="ACTIVE")


@pytest.mark.django_db
@pytest.mark.parametrize("remaining,decision", [(90, "CANDIDATE"), (91, "NOT_CANDIDATE"),
                                                  (1, "CANDIDATE"), (0, "NOT_CANDIDATE")])
def test_contract_window_boundaries_are_authority_driven(auction_context, remaining, decision):
    user, beneficiary, rule = auction_context
    space = _space(str(8100 + remaining))
    today = jdatetime.date(1405, 7, 1)
    end = jdatetime.date.fromgregorian(date=today.togregorian() + __import__('datetime').timedelta(days=remaining))
    Contract.objects.create(space=space, number="C", start_date="1405/01/01", end_date=end.strftime("%Y/%m/%d"),
        amount_rial=Decimal("500000000"), beneficiary=beneficiary)
    Appraisal.objects.create(space=space, appraisal_date="1405/06/01", amount_rial=Decimal("500000000"), is_current=True)
    result = evaluate_space(space=space, on_date="1405/07/01", actor=user, rule=rule)
    assert result.decision == decision


@pytest.mark.django_db
def test_missing_appraisal_is_review_not_silent_exclusion(auction_context):
    user, _, rule = auction_context
    result = evaluate_space(space=_space("8201"), on_date="1405/07/01", actor=user, rule=rule)
    assert result.decision == "REVIEW_REQUIRED"
    assert result.reason_codes == ["REVIEW_MISSING_APPRAISAL"]


@pytest.mark.django_db
def test_out_of_cycle_space_is_not_auto_candidate(auction_context):
    user, _, rule = auction_context
    space = _space("8202"); space.status = "OUT_OF_CYCLE"; space.save(update_fields=["status"])
    result = evaluate_space(space=space, on_date="1405/07/01", actor=user, rule=rule)
    assert result.decision == "NOT_CANDIDATE"
    assert result.reason_codes == ["NOT_CANDIDATE_SPACE_OUT_OF_CYCLE"]



@pytest.mark.django_db
def test_auction_uses_only_current_appraisal(auction_context):
    user,_,rule=auction_context
    space=_space("8290")
    Appraisal.objects.create(space=space,appraisal_date="1405/06/01",amount_rial=Decimal("900000000"),is_current=False)
    result=evaluate_space(space=space,on_date="1405/07/01",actor=user,rule=rule)
    assert result.decision=="REVIEW_REQUIRED"
    assert result.reason_codes==["REVIEW_MISSING_APPRAISAL"]


@pytest.mark.django_db
def test_appraisal_expiring_before_planned_auction_is_action_required(auction_context):
    user,_,rule=auction_context
    space=_space("8291")
    Appraisal.objects.create(space=space,appraisal_date="1405/01/15",amount_rial=Decimal("500000000"),is_current=True)
    result=evaluate_space(
        space=space,on_date="1405/07/01",auction_date="1405/08/01",actor=user,rule=rule
    )
    assert result.decision=="REVIEW_REQUIRED"
    assert result.readiness=="ACTION_REQUIRED"
    assert result.reason_codes==["ACTION_APPRAISAL_EXPIRES_BEFORE_AUCTION"]


@pytest.mark.django_db
def test_missing_rule_for_evaluation_year_fails_safe(db):
    user=get_user_model().objects.create_user("auction-no-rule",password="A-very-safe-password")
    AuctionRule.objects.create(
        version="1404.1",effective_year=1404,contract_window_min_days=1,contract_window_max_days=90,
        minor_ceiling_rial=Decimal("350000000"),medium_ceiling_rial=Decimal("3500000000"),
        appraisal_valid_months=6,active=True,change_reason="سال قبل",approved_by=user,
    )
    with pytest.raises(Exception) as exc:
        evaluate_space(space=_space("8292"),on_date="1405/07/01",actor=user)
    assert "برای سال ارزیابی" in str(exc.value)


@pytest.mark.django_db
def test_conflicting_authorized_instructions_require_review(auction_context):
    user,_,rule=auction_context
    user.is_staff=True;user.save(update_fields=["is_staff"])
    space=_space("8293")
    Appraisal.objects.create(space=space,appraisal_date="1405/06/01",amount_rial=Decimal("500000000"),is_current=True)
    AuctionInstruction.objects.create(
        space=space,source="MANAGER",direction="INCLUDE",reason="دستور مدیر",reference="M-1",
        effective_from="1405/07/01",created_by=user,
    )
    AuctionInstruction.objects.create(
        space=space,source="COMMISSION",direction="EXCLUDE",reason="تصمیم کمیسیون",reference="C-1",
        effective_from="1405/07/01",created_by=user,
    )
    result=evaluate_space(space=space,on_date="1405/07/10",actor=user,rule=rule)
    assert result.decision=="REVIEW_REQUIRED"
    assert result.reason_codes==["CONFLICTING_AUTHORIZED_INSTRUCTIONS"]
    assert len(result.snapshot["override_state"])==2


@pytest.mark.django_db
def test_manual_include_and_exclude_are_audited_equal_authority(client,auction_context):
    user,_,rule=auction_context
    user.is_staff=True;user.save(update_fields=["is_staff"])
    client.force_login(user)
    include_space=_space("8294")
    Appraisal.objects.create(space=include_space,appraisal_date="1405/06/01",amount_rial=Decimal("100000000"),is_current=True)
    response=client.post("/auctions/instructions/new/",{
        "space":include_space.pk,"source":"MANAGER","direction":"INCLUDE",
        "reason":"دستور مصوب مدیر","reference":"M-2","effective_from":"1405/07/01",
    })
    assert response.status_code==302
    result=evaluate_space(space=include_space,on_date="1405/07/10",actor=user,rule=rule)
    assert result.decision=="CANDIDATE"
    assert result.reason_codes[0]=="INCLUDED_BY_MANUAL_OVERRIDE"

    exclude_space=_space("8295")
    Appraisal.objects.create(space=exclude_space,appraisal_date="1405/06/01",amount_rial=Decimal("500000000"),is_current=True)
    AuctionInstruction.objects.create(
        space=exclude_space,source="MANAGER",direction="EXCLUDE",reason="دستور معتبر",reference="M-3",
        effective_from="1405/07/01",created_by=user,
    )
    result=evaluate_space(space=exclude_space,on_date="1405/07/10",actor=user,rule=rule)
    assert result.decision=="NOT_CANDIDATE"
    assert result.reason_codes==["BLOCKED_BY_MANUAL_EXCLUSION"]
