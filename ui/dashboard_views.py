from urllib.parse import urlencode

from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import render
from django.utils import timezone

from domains.operations.models import Alert, AuctionEvaluation, WorkflowInstance
from domains.properties.models import Center, CommercialSpace, MotherProperty, Region
from domains.registry.models import Discrepancy
from queries.spaces import filter_spaces
from services.dates import today_jalali


_SCOPE_KEYS = ("region_id", "center_id", "status")


def _scope_from_request(request):
    scope = {}
    for key in _SCOPE_KEYS:
        values = [value for value in request.GET.getlist(key) if value]
        if values:
            scope[key] = values
    usage = (request.GET.get("usage") or "").strip()
    if usage:
        scope["usage"] = usage
        scope["usage_op"] = "contains"
    return scope


def _scope_pairs(scope):
    pairs = []
    for key in _SCOPE_KEYS:
        for value in scope.get(key, []):
            pairs.append((key, value))
    if scope.get("usage"):
        pairs.append(("usage", scope["usage"]))
        pairs.append(("usage_op", "contains"))
    return pairs


def _scope_query(scope, **extra):
    pairs = _scope_pairs(scope)
    for key, value in extra.items():
        if value is None:
            continue
        if isinstance(value, (list, tuple)):
            pairs.extend((key, item) for item in value)
        else:
            pairs.append((key, value))
    return urlencode(pairs)


def _latest_auction_counts(space_ids):
    latest = {}
    for item in (
        AuctionEvaluation.objects.select_related("space")
        .filter(space_id__in=space_ids)
        .order_by("space_id", "-evaluated_at", "-pk")
    ):
        latest.setdefault(item.space_id, item)
    rows = list(latest.values())
    return {
        "candidate": sum(1 for item in rows if item.decision == "CANDIDATE"),
        "review": sum(1 for item in rows if item.decision == "REVIEW_REQUIRED"),
        "action": sum(1 for item in rows if item.readiness == "ACTION_REQUIRED"),
    }


def _scope_summary(scope):
    parts = []
    region_ids = scope.get("region_id", [])
    center_ids = scope.get("center_id", [])
    if region_ids:
        names = list(Region.objects.filter(pk__in=region_ids).order_by("code").values_list("name", flat=True))
        if names:
            parts.append("مناطق: " + "، ".join(names))
    if center_ids:
        names = list(Center.objects.filter(pk__in=center_ids).order_by("name").values_list("name", flat=True))
        if names:
            parts.append("مراکز: " + "، ".join(names))
    if scope.get("usage"):
        parts.append("کاربری: " + scope["usage"])
    statuses = scope.get("status", [])
    if statuses:
        labels = dict(CommercialSpace.Status.choices)
        parts.append("وضعیت: " + "، ".join(labels.get(value, value) for value in statuses))
    return parts


@login_required
def dashboard(request):
    scope = _scope_from_request(request)
    scope_qs = filter_spaces(scope)
    scope_ids = list(scope_qs.values_list("pk", flat=True))

    active_count = scope_qs.filter(status=CommercialSpace.Status.ACTIVE).count()
    inactive_count = scope_qs.filter(status=CommercialSpace.Status.OUT_OF_CYCLE).count()

    active_scope = dict(scope)
    active_scope["status"] = [CommercialSpace.Status.ACTIVE]
    current_contract_count = filter_spaces({**active_scope, "current_contract": "present"}).count()
    without_contract_count = filter_spaces({**active_scope, "current_contract": "empty"}).count()
    current_appraisal_count = filter_spaces({**active_scope, "current_appraisal": "present"}).count()
    without_appraisal_count = filter_spaces({**active_scope, "current_appraisal": "empty"}).count()
    contract_today_count = filter_spaces({**active_scope, "contract_bucket": "TODAY"}).count()
    contract_1_30_count = filter_spaces({**active_scope, "contract_bucket": "1_30"}).count()
    contract_31_60_count = filter_spaces({**active_scope, "contract_bucket": "31_60"}).count()
    contract_61_90_count = filter_spaces({**active_scope, "contract_bucket": "61_90"}).count()
    long_term_contract_count = filter_spaces({**active_scope, "contract_bucket": "LONG_TERM"}).count()

    active_annotated = filter_spaces(active_scope)
    with_beneficiary_count = active_annotated.filter(current_beneficiary_name__isnull=False).count()
    without_beneficiary_count = active_annotated.filter(current_beneficiary_name__isnull=True).count()

    region_rows = list(
        scope_qs.filter(status=CommercialSpace.Status.ACTIVE)
        .exclude(region=None)
        .values("region__name")
        .annotate(total=Count("id"))
        .order_by("-total", "region__name")[:5]
    )
    maximum = max((row["total"] for row in region_rows), default=1)
    for row in region_rows:
        row["percent"] = round(row["total"] * 100 / maximum)

    auction = _latest_auction_counts(scope_ids)
    open_alerts = Alert.objects.filter(space_id__in=scope_ids, status=Alert.Status.OPEN)
    open_workflows = WorkflowInstance.objects.filter(space_id__in=scope_ids, state=WorkflowInstance.State.OPEN)
    today = today_jalali()
    overdue_workflows = open_workflows.exclude(due_date="").filter(due_date__lt=today).count()
    overdue_alerts = open_alerts.exclude(due_date="").filter(due_date__lt=today).count()

    links = {
        "active": _scope_query(scope, status=[CommercialSpace.Status.ACTIVE]),
        "inactive": _scope_query(scope, status=[CommercialSpace.Status.OUT_OF_CYCLE]),
        "contract_present": _scope_query(active_scope, current_contract="present"),
        "contract_empty": _scope_query(active_scope, current_contract="empty"),
        "appraisal_present": _scope_query(active_scope, current_appraisal="present"),
        "appraisal_empty": _scope_query(active_scope, current_appraisal="empty"),
        "contract_today": _scope_query(active_scope, contract_bucket="TODAY"),
        "contract_1_30": _scope_query(active_scope, contract_bucket="1_30"),
        "contract_31_60": _scope_query(active_scope, contract_bucket="31_60"),
        "contract_61_90": _scope_query(active_scope, contract_bucket="61_90"),
        "contract_long": _scope_query(active_scope, contract_bucket="LONG_TERM"),
        "action_all": _scope_query(scope),
        "action_alerts": _scope_query(scope, kind="alerts"),
        "action_critical": _scope_query(scope, kind="alerts", priority=Alert.Priority.CRITICAL),
        "action_alerts_overdue": _scope_query(scope, kind="alerts", overdue="1"),
        "action_workflows": _scope_query(scope, kind="workflows"),
        "action_workflows_overdue": _scope_query(scope, kind="workflows", overdue="1"),
    }

    context = {
        "scope_count": scope_qs.count(),
        "active_count": active_count,
        "inactive_count": inactive_count,
        "property_count": MotherProperty.objects.count(),
        "discrepancy_count": Discrepancy.objects.exclude(status=Discrepancy.Status.RESOLVED).count(),
        "alert_count": open_alerts.count(),
        "critical_alert_count": open_alerts.filter(priority=Alert.Priority.CRITICAL).count(),
        "high_alert_count": open_alerts.filter(priority=Alert.Priority.HIGH).count(),
        "overdue_alert_count": overdue_alerts,
        "open_workflow_count": open_workflows.count(),
        "overdue_workflow_count": overdue_workflows,
        "current_contract_count": current_contract_count,
        "without_contract_count": without_contract_count,
        "current_appraisal_count": current_appraisal_count,
        "without_appraisal_count": without_appraisal_count,
        "contract_today_count": contract_today_count,
        "contract_1_30_count": contract_1_30_count,
        "contract_31_60_count": contract_31_60_count,
        "contract_61_90_count": contract_61_90_count,
        "long_term_contract_count": long_term_contract_count,
        "with_beneficiary_count": with_beneficiary_count,
        "without_beneficiary_count": without_beneficiary_count,
        "auction_candidate_count": auction["candidate"],
        "auction_review_count": auction["review"],
        "auction_action_count": auction["action"],
        "region_rows": region_rows,
        "regions": Region.objects.order_by("code", "name"),
        "centers": Center.objects.order_by("name"),
        "selected_regions": scope.get("region_id", []),
        "selected_centers": scope.get("center_id", []),
        "selected_statuses": scope.get("status", []),
        "selected_usage": scope.get("usage", ""),
        "scope_summary": _scope_summary(scope),
        "links": links,
        "refreshed_at": timezone.now(),
    }
    return render(request, "ui/dashboard.html", context)
