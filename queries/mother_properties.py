"""Canonical query for the Mother Property first-class domain."""
from django.db.models import Count, Q, Case, When, Value, IntegerField
from django.db.models.functions import Cast, Replace
from domains.properties.models import MotherProperty

SORTS={'identifier':'identifier','name':'name','region':'region_numeric','area':'area','space_count':'space_count'}

def filter_mother_properties(params):
    region='region__code'
    for fa,en in zip('۰۱۲۳۴۵۶۷۸۹','0123456789'):region=Replace(region,Value(fa),Value(en))
    qs=MotherProperty.objects.select_related('region').annotate(space_count=Count('space_links',distinct=True),region_numeric=Case(When(region__code__regex=r'^[0-9۰-۹]+$',then=Cast(region,IntegerField())),default=Value(999),output_field=IntegerField()))
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
    return qs.order_by(*(ordering or ['region_numeric','name','identifier']))
