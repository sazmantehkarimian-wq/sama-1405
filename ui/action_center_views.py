from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render

from domains.operations.models import Alert, WorkflowInstance
from queries.spaces import filter_spaces
from services.dates import today_jalali
from ui.dashboard_views import _scope_from_request, _scope_summary


@login_required
def action_center(request):
    scope = _scope_from_request(request)
    space_ids = filter_spaces(scope).values_list("pk", flat=True)
    today = today_jalali()
    kind = (request.GET.get("kind") or "all").strip()

    alerts = Alert.objects.select_related("space", "assigned_to").filter(
        space_id__in=space_ids,
        status=Alert.Status.OPEN,
    )
    workflows = WorkflowInstance.objects.select_related("space", "created_by").filter(
        space_id__in=space_ids,
        state=WorkflowInstance.State.OPEN,
    )

    priority = (request.GET.get("priority") or "").strip()
    if priority in Alert.Priority.values:
        alerts = alerts.filter(priority=priority)
    overdue = request.GET.get("overdue") == "1"
    if overdue:
        alerts = alerts.exclude(due_date="").filter(due_date__lt=today)
        workflows = workflows.exclude(due_date="").filter(due_date__lt=today)

    q = (request.GET.get("q") or "").strip()
    if q:
        alerts = alerts.filter(
            Q(space__code__iexact=q) | Q(space__name__icontains=q) |
            Q(subject__icontains=q) | Q(reason__icontains=q)
        )
        workflows = workflows.filter(
            Q(space__code__iexact=q) | Q(space__name__icontains=q) |
            Q(title__icontains=q) | Q(next_action__icontains=q)
        )

    if kind == "alerts":
        workflows = workflows.none()
    elif kind == "workflows":
        alerts = alerts.none()

    alert_page = Paginator(alerts.order_by("priority", "due_date", "pk"), 50).get_page(request.GET.get("alert_page"))
    workflow_page = Paginator(workflows.order_by("due_date", "pk"), 50).get_page(request.GET.get("workflow_page"))

    return render(request, "ui/action_center.html", {
        "scope_summary": _scope_summary(scope),
        "alert_page": alert_page,
        "workflow_page": workflow_page,
        "alert_count": alerts.count(),
        "workflow_count": workflows.count(),
        "critical_count": alerts.filter(priority=Alert.Priority.CRITICAL).count(),
        "high_count": alerts.filter(priority=Alert.Priority.HIGH).count(),
        "overdue_alert_count": alerts.exclude(due_date="").filter(due_date__lt=today).count(),
        "overdue_workflow_count": workflows.exclude(due_date="").filter(due_date__lt=today).count(),
        "priorities": Alert.Priority.choices,
        "kind": kind,
        "selected_priority": priority,
        "selected_overdue": overdue,
        "q": q,
    })
