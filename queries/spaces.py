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
    if statuses:
        qs = qs.filter(status__in=statuses)
    if regions:
        qs = qs.filter(region_id__in=regions)
    if centers:
        qs = qs.filter(center_id__in=centers)

    qs = _text(qs, "code", params.get("code", ""), params.get("code_op", "equals"))
    qs = _text(qs, "current_usage", params.get("usage", ""), params.get("usage_op", "contains"))
    qs = _text(qs, "beneficiary_assignments__beneficiary__name", params.get("beneficiary", ""),
               params.get("beneficiary_op", "contains"))
    qs = _text(qs, "contracts__number", params.get("contract", ""), params.get("contract_op", "contains"))

    presence = params.get("address_presence")
    if presence == "empty":
        qs = qs.filter(Q(address="") | Q(address__isnull=True))
    elif presence == "nonempty":
        qs = qs.exclude(Q(address="") | Q(address__isnull=True))

    try:
        if params.get("area_min"):
            qs = qs.filter(area__gte=Decimal(params["area_min"]))
        if params.get("area_max"):
            qs = qs.filter(area__lte=Decimal(params["area_max"]))
    except (InvalidOperation, ValueError):
        return qs.none()

    allowed = {"code", "name", "status", "area", "current_usage"}
    requested = _values(params, "sort") or ["code"]
    ordering = [item for item in requested if item.lstrip("-") in allowed][:3] or ["code"]
    return qs.distinct().order_by(*ordering)
