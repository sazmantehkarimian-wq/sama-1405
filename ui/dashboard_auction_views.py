from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from domains.operations.models import AuctionEvaluation
from queries.spaces import filter_spaces
from ui.dashboard_views import _scope_from_request, _scope_summary


@login_required
def auction_drilldown(request):
    scope = _scope_from_request(request)
    space_ids = filter_spaces(scope).values_list("pk", flat=True)
    latest = {}
    for item in (
        AuctionEvaluation.objects.select_related("space", "rule")
        .filter(space_id__in=space_ids)
        .order_by("space_id", "-evaluated_at", "-pk")
    ):
        latest.setdefault(item.space_id, item)

    mode = (request.GET.get("mode") or "all").strip()
    rows = list(latest.values())
    if mode == "candidate":
        rows = [item for item in rows if item.decision == "CANDIDATE"]
    elif mode == "review":
        rows = [item for item in rows if item.decision == "REVIEW_REQUIRED"]
    elif mode == "action":
        rows = [item for item in rows if item.readiness == "ACTION_REQUIRED"]

    rows.sort(key=lambda item: (item.space.code, item.pk))
    return render(request, "ui/dashboard_auction_drilldown.html", {
        "rows": rows,
        "mode": mode,
        "scope_summary": _scope_summary(scope),
        "row_count": len(rows),
    })
