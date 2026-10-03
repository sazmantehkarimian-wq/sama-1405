import pytest
from django.contrib.auth import get_user_model

from domains.operations.models import AuctionEvaluation, AuctionRule
from domains.properties.models import CommercialSpace, Region


@pytest.mark.django_db
def test_scoped_auction_drilldown_matches_dashboard_latest_evaluation(client):
    user=get_user_model().objects.create_user('dashboard-auction',password='A-very-safe-password')
    client.force_login(user)
    r1=Region.objects.create(code='6',name='منطقه ۶')
    r2=Region.objects.create(code='7',name='منطقه ۷')
    s1=CommercialSpace.objects.create(code='9701',name='فضای مزایده یک',status='ACTIVE',region=r1)
    s2=CommercialSpace.objects.create(code='9702',name='فضای مزایده دو',status='ACTIVE',region=r2)
    rule=AuctionRule.objects.create(
        version='DASH-1405',effective_year=1405,
        minor_ceiling_rial=1000000,medium_ceiling_rial=5000000,
        appraisal_valid_months=6,active=True,change_reason='آزمون داشبورد',approved_by=user,
    )

    AuctionEvaluation.objects.create(
        space=s1,rule=rule,decision='CANDIDATE',readiness='READY',
        reason_codes=['OLD'],snapshot={'version':1},evaluated_by=user,
    )
    AuctionEvaluation.objects.create(
        space=s1,rule=rule,decision='REVIEW_REQUIRED',readiness='ACTION_REQUIRED',
        reason_codes=['MISSING_DATA'],snapshot={'version':2},evaluated_by=user,
    )
    AuctionEvaluation.objects.create(
        space=s2,rule=rule,decision='CANDIDATE',readiness='READY',
        reason_codes=['OTHER_REGION'],snapshot={},evaluated_by=user,
    )

    dashboard=client.get('/',{'region_id':str(r1.pk)})
    assert dashboard.status_code==200
    assert dashboard.context['auction_review_count']==1
    assert dashboard.context['auction_action_count']==1
    assert dashboard.context['auction_candidate_count']==0

    review=client.get('/dashboard/auctions/',{'region_id':str(r1.pk),'mode':'review'})
    assert review.status_code==200
    assert review.context['row_count']==dashboard.context['auction_review_count']==1
    body=review.content.decode()
    assert '9701' in body
    assert '9702' not in body
    assert 'MISSING_DATA' in body

    action=client.get('/dashboard/auctions/',{'region_id':str(r1.pk),'mode':'action'})
    assert action.status_code==200
    assert action.context['row_count']==dashboard.context['auction_action_count']==1
