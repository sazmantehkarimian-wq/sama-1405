from django.db.models import Q

from domains.properties.models import CommercialSpace, MotherProperty


def _values(params, key):
    if hasattr(params, "getlist"):
        return [v for v in params.getlist(key) if v]
    value = params.get(key)
    return value if isinstance(value, list) else ([value] if value else [])


def search_spaces(params):
    qs = CommercialSpace.objects.select_related("region", "center").all()
    q = (params.get("q") or "").strip()
    if q:
        qs = qs.filter(
            Q(code__iexact=q)
            | Q(name__icontains=q)
            | Q(address__icontains=q)
            | Q(current_usage__icontains=q)
            | Q(proposed_activity__icontains=q)
            | Q(activity_group__icontains=q)
        )
    if statuses := _values(params, "status"):
        qs = qs.filter(status__in=statuses)
    if regions := _values(params, "region"):
        qs = qs.filter(region_id__in=regions)
    if centers := _values(params, "center"):
        qs = qs.filter(center_id__in=centers)
    if params.get("special") == "1":
        qs = qs.filter(center__is_special=True)
    elif params.get("special") == "0":
        qs = qs.filter(Q(center__is_special=False) | Q(center__isnull=True))
    if value := (params.get("usage") or "").strip():
        qs = qs.filter(current_usage__icontains=value)
    if value := (params.get("activity") or "").strip():
        qs = qs.filter(Q(proposed_activity__icontains=value) | Q(activity_group__icontains=value))
    if value := (params.get("scope") or "").strip():
        qs = qs.filter(organizational_scope__icontains=value)
    if value := (params.get("asset_type") or "").strip():
        qs = qs.filter(asset_type__icontains=value)
    return qs.order_by("region__name", "center__name", "code").distinct()


def search_mother_properties(params):
    qs = MotherProperty.objects.select_related("region").all()
    q = (params.get("q") or "").strip()
    if q:
        qs = qs.filter(Q(identifier__iexact=q) | Q(name__icontains=q) | Q(address__icontains=q) | Q(primary_usage__icontains=q))
    if regions := _values(params, "region"):
        qs = qs.filter(region_id__in=regions)
    if value := (params.get("usage") or "").strip():
        qs = qs.filter(Q(primary_usage__icontains=value) | Q(usage_group__icontains=value))
    if value := (params.get("center_type") or "").strip():
        qs = qs.filter(center_type__icontains=value)
    return qs.order_by("region__name", "name", "identifier")
