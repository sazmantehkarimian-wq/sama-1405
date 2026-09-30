def effective_contract(queryset,on_date):
 return queryset.filter(start_date__lte=on_date,end_date__gte=on_date).exclude(status__in=['باطل','فسخ‌شده']).order_by('-start_date').first()
