"""Canonical CommercialSpace query/filter implementation used by UI and exports."""
from decimal import Decimal, InvalidOperation

from django.db.models import Q

from domains.properties.models import CommercialSpace


TEXT_OPERATORS = {"contains": "icontains", "equals": "iexact", "starts": "istartswith"}


def _values(params, key):
    if hasattr(params, "getlist"):
        return [value for value in params.getlist(key) if value]
    value = params.get(key, [])
    return value if isinstance(value, list) else ([value] if value else [])


def _text(qs, field, value, operator):
    value = (value or "").strip()
    if not value:
        return qs
    lookup = TEXT_OPERATORS.get(operator, "icontains")
    return qs.filter(**{f"{field}__{lookup}": value})


def _text_q(field, value, operator):
    value = (value or "").strip()
    if not value:
        return None
    return Q(**{f"{field}__{TEXT_OPERATORS.get(operator, 'icontains')}": value})


def filter_spaces(params):
    qs = CommercialSpace.objects.select_related("region", "center").all()
    q = params.get("q", "").strip()
    if q:
        qs = qs.filter(
            Q(code__iexact=q) | Q(name__icontains=q) | Q(current_usage__icontains=q)
            | Q(beneficiary_assignments__beneficiary__name__icontains=q)
            | Q(contracts__number__icontains=q)
        ).distinct()

    statuses = _values(params, "status")
    regions = _values(params, "region_id")
    centers = _values(params, "center_id")
    clauses = []
    if statuses: clauses.append(Q(status__in=statuses))
    if regions: clauses.append(Q(region_id__in=regions))
    if centers: clauses.append(Q(center_id__in=centers))
    for field, value_key, operator_key, fallback in (
        ("code", "code", "code_op", "equals"),
        ("current_usage", "usage", "usage_op", "contains"),
        ("beneficiary_assignments__beneficiary__name", "beneficiary", "beneficiary_op", "contains"),
        ("contracts__number", "contract", "contract_op", "contains"),
    ):
        clause = _text_q(field, params.get(value_key, ""), params.get(operator_key, fallback))
        if clause is not None: clauses.append(clause)
    presence = params.get("address_presence")
    if presence == "empty":
        clauses.append(Q(address="") | Q(address__isnull=True))
    elif presence == "nonempty":
        clauses.append(~(Q(address="") | Q(address__isnull=True)))

    try:
        if params.get("area_min"):
            clauses.append(Q(area__gte=Decimal(params["area_min"])))
        if params.get("area_max"):
            clauses.append(Q(area__lte=Decimal(params["area_max"])))
    except (InvalidOperation, ValueError):
        return qs.none()

    if clauses:
        combined = clauses[0]
        for clause in clauses[1:]:
            combined = (combined | clause) if params.get("logic", "and").lower() == "or" else (combined & clause)
        qs = qs.filter(combined)

    allowed = {"code", "name", "status", "area", "current_usage"}
    requested = _values(params, "sort") or ["code"]
    ordering = [item for item in requested if item.lstrip("-") in allowed][:3] or ["code"]
    return qs.distinct().order_by(*ordering)
