from decimal import Decimal

import jdatetime
import pytest
from django.contrib.auth import get_user_model

from domains.contracts.models import Contract
from domains.operations.models import Appraisal, AuctionRule
from domains.properties.models import CommercialSpace
from domains.registry.models import ImportBatch, SourceFile
from services.auctions import evaluate_space


@pytest.fixture
def auction_context(db):
    user = get_user_model().objects.create_user("auction-owner", password="A-very-safe-password")
    batch = ImportBatch.objects.create(source_package="test.zip", package_sha256="a" * 64)
    source = SourceFile.objects.create(batch=batch, filename="source.xlsx", sha256="b" * 64, byte_size=1)
    rule = AuctionRule.objects.create(version="1405.1", effective_year=1405,
        contract_window_min_days=1, contract_window_max_days=90,
        minor_ceiling_rial=Decimal("350000000"), medium_ceiling_rial=Decimal("3500000000"),
        appraisal_valid_months=6, active=True, change_reason="مرز مصوب مرجع ۱۴۰۵", approved_by=user)
    return user, source, rule


def _space(code):
    return CommercialSpace.objects.create(code=code, name="فضا", status="ACTIVE", source_row=1,
                                           source_classification="authority")


@pytest.mark.django_db
@pytest.mark.parametrize("remaining,decision", [(90, "CANDIDATE"), (91, "NOT_CANDIDATE"),
                                                  (1, "CANDIDATE"), (0, "NOT_CANDIDATE")])
def test_contract_window_boundaries_are_authority_driven(auction_context, remaining, decision):
    user, source, rule = auction_context
    space = _space(f"B-{remaining}")
    today = jdatetime.date(1405, 7, 1)
    end = jdatetime.date.fromgregorian(date=today.togregorian() + __import__('datetime').timedelta(days=remaining))
    Contract.objects.create(space=space, number="C", start_date="1405/01/01", end_date=end.strftime("%Y/%m/%d"),
        amount_rial=Decimal("500000000"), source_file=source, source_row=1)
    Appraisal.objects.create(space=space, appraisal_date="1405/06/01", amount_rial=Decimal("500000000"),
        source_file=source, source_row=1)
    result = evaluate_space(space=space, on_date="1405/07/01", actor=user, rule=rule)
    assert result.decision == decision


@pytest.mark.django_db
def test_missing_appraisal_is_review_not_silent_exclusion(auction_context):
    user, _, rule = auction_context
    result = evaluate_space(space=_space("MISSING"), on_date="1405/07/01", actor=user, rule=rule)
    assert result.decision == "REVIEW_REQUIRED"
    assert result.reason_codes == ["REVIEW_MISSING_APPRAISAL"]


@pytest.mark.django_db
def test_out_of_cycle_space_is_not_auto_candidate(auction_context):
    user, _, rule = auction_context
    space = _space("OUT"); space.status = "OUT_OF_CYCLE"; space.save(update_fields=["status"])
    result = evaluate_space(space=space, on_date="1405/07/01", actor=user, rule=rule)
    assert result.decision == "NOT_CANDIDATE"
    assert result.reason_codes == ["NOT_CANDIDATE_SPACE_OUT_OF_CYCLE"]
