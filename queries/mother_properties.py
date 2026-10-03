"""Canonical query for the Mother Property first-class domain."""
from django.db.models import Count, Q
from domains.properties.models import MotherProperty

SORTS={'identifier':'identifier','name':'name','region':'region__name','area':'area','space_count':'space_count'}

def filter_mother_properties(params):
    qs=MotherProperty.objects.select_related('region').annotate(space_count=Count('space_links',distinct=True))
    q=(params.get('q','') or '').strip()
    if q:qs=qs.filter(Q(identifier__icontains=q)|Q(name__icontains=q)|Q(address__icontains=q))
    if params.get('identifier'):qs=qs.filter(identifier__icontains=params['identifier'].strip())
    if params.get('property_name'):qs=qs.filter(name__icontains=params['property_name'].strip())
    if params.get('region_id'):qs=qs.filter(region_id=params['region_id'])
    if params.get('usage'):qs=qs.filter(Q(primary_usage__icontains=params['usage'])|Q(usage_group__icontains=params['usage']))
    requested=params.getlist('sort') if hasattr(params,'getlist') else params.get('sort',[])
    if isinstance(requested,str):requested=[requested]
    ordering=[]
    for item in requested[:3]:
        descending=item.startswith('-');key=item.lstrip('-')
        if key in SORTS:ordering.append(('-' if descending else '')+SORTS[key])
    return qs.order_by(*(ordering or ['identifier']))
