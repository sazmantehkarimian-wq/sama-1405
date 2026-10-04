"""Canonical CommercialSpace query/filter implementation used by UI and exports."""
from decimal import Decimal, InvalidOperation

from django.db.models import Q, Case, When, Value, IntegerField, CharField
from django.db.models.functions import Cast, Coalesce, Replace

from domains.properties.models import CommercialSpace


TEXT_OPERATORS = {"contains": "icontains", "equals": "iexact", "starts": "istartswith"}

def _latin_digits(expression):
    for fa,en in zip("۰۱۲۳۴۵۶۷۸۹","0123456789"):
        expression=Replace(expression,Value(fa),Value(en))
    return expression

def _ordered(qs):
    """Add non-destructive canonical sort keys shared by list, reports and pickers."""
    normalized_code=_latin_digits('code');normalized_region=_latin_digits('region__code')
    return qs.annotate(
        management_group=Case(When(center__is_special=True,then=Value(2)),default=Value(1),output_field=IntegerField()),
        geographic_region_numeric=Case(When(region__code__regex=r'^[0-9۰-۹]+$',then=Cast(normalized_region,IntegerField())),default=Value(999),output_field=IntegerField()),
        center_sort_name=Coalesce('center__name','name',output_field=CharField()),
        code_is_non_numeric=Case(When(code__regex=r'^[0-9۰-۹]+$',then=Value(0)),default=Value(1),output_field=IntegerField()),
        code_numeric=Case(When(code__regex=r'^[0-9۰-۹]+$',then=Cast(normalized_code,IntegerField())),default=Value(2147483647),output_field=IntegerField()),
    )


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
    qs = _ordered(CommercialSpace.objects.select_related("region", "center").prefetch_related("beneficiary_assignments__beneficiary").all())
    q = params.get("q", "").strip()
    if q:
        qs = qs.filter(
            Q(code__iexact=q) | Q(name__icontains=q) | Q(current_usage__icontains=q)
            | Q(beneficiary_assignments__beneficiary__name__icontains=q)
            | Q(contracts__number__icontains=q)
        ).annotate(search_rank=Case(When(code__iexact=q,then=Value(0)),When(code__istartswith=q,then=Value(1)),When(name__iexact=q,then=Value(2)),default=Value(3),output_field=IntegerField())).distinct()

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
    contract_presence = params.get("contract_presence")
    if contract_presence == "empty": clauses.append(Q(contracts__isnull=True))
    elif contract_presence == "nonempty": clauses.append(Q(contracts__isnull=False))
    appraisal_presence = params.get("appraisal_presence")
    if appraisal_presence == "empty": clauses.append(Q(appraisals__isnull=True))
    elif appraisal_presence == "nonempty": clauses.append(Q(appraisals__isnull=False))

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

    requested = _values(params, "sort")
    mappings={"code":("code_is_non_numeric","code_numeric","code"),"region":("geographic_region_numeric","region__name"),"center":("center_sort_name",),"name":("name",),"status":("status",),"area":("area",),"current_usage":("current_usage",),"beneficiary":("beneficiary_assignments__beneficiary__name",)}
    ordering=[]
    for item in requested[:3]:
        desc=item.startswith('-');key=item.lstrip('-')
        if key=='code':ordering.extend(['code_is_non_numeric',('-' if desc else '')+'code_numeric',('-' if desc else '')+'code'])
        elif key in mappings:ordering.extend([('-' if desc else '')+field for field in mappings[key]])
    if not ordering:ordering=(['search_rank'] if q else [])+['management_group','geographic_region_numeric','center_sort_name','code_is_non_numeric','code_numeric','code']
    return qs.distinct().order_by(*ordering)
