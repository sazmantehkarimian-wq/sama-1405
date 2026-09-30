from django.db.models import Q
from domains.properties.models import CommercialSpace
def filter_spaces(params):
 qs=CommercialSpace.objects.select_related('region','center').all()
 q=params.get('q','').strip()
 if q: qs=qs.filter(Q(code__iexact=q)|Q(name__icontains=q)|Q(current_usage__icontains=q)|Q(beneficiary_assignments__beneficiary__name__icontains=q)|Q(contracts__number__icontains=q)).distinct()
 for key in ('status','region_id','center_id'):
  if params.get(key): qs=qs.filter(**{key:params[key]})
 if params.get('code'): qs=qs.filter(code__iexact=params['code'].strip())
 if params.get('usage'): qs=qs.filter(current_usage__icontains=params['usage'].strip())
 allowed={'code','name','status','area'}; sort=params.get('sort','code').lstrip('-'); order=params.get('sort','code') if sort in allowed else 'code'
 return qs.order_by(order)
