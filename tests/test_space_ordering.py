import pytest
from django.http import QueryDict
from domains.properties.models import Center,CommercialSpace,Region,MotherProperty
from queries.spaces import filter_spaces
from queries.mother_properties import filter_mother_properties
pytestmark=pytest.mark.django_db

def make_space(code,region,center):
 return CommercialSpace.objects.create(code=str(code),name=f'فضای {code}',status='ACTIVE',region=region,center=center,source_row=int(str(code).strip('P-') or 1),source_classification='authority')

def params(**values):
 q=QueryDict('',mutable=True)
 for key,value in values.items():q.setlist(key,value if isinstance(value,list) else [value])
 return q

def test_explicit_global_code_sort_is_numeric_not_lexicographic():
 region=Region.objects.create(code='1',name='منطقه ۱');center=Center.objects.create(name='الف',region=region)
 expected=['1','2','9','10','11','12','13','99','100','101','121','129','130']
 for code in reversed(expected):make_space(code,region,center)
 assert list(filter_spaces(params(sort=['code'])).values_list('code',flat=True))==expected

def test_default_regions_centers_then_special_centers_without_duplicates():
 r1=Region.objects.create(code='1',name='منطقه ۱');r2=Region.objects.create(code='2',name='منطقه ۲');r22=Region.objects.create(code='22',name='منطقه ۲۲')
 a=Center.objects.create(name='مرکز الف',region=r1);b=Center.objects.create(name='مرکز ب',region=r1)
 ordinary=[make_space('10',r1,a),make_space('2',r1,a),make_space('1',r1,b),make_space('3',r2,Center.objects.create(name='مرکز ج',region=r2)),make_space('4',r22,Center.objects.create(name='مرکز د',region=r22))]
 special=Center.objects.create(name='مرکز خاص',region=r1,is_special=True)
 s1=make_space('20',r1,special);s22=make_space('21',r22,special);unknown=make_space('22',None,special)
 ids=list(filter_spaces(params()).values_list('id',flat=True));codes=list(filter_spaces(params()).values_list('code',flat=True))
 assert codes==['2','10','1','3','4','20','21','22']
 assert len(ids)==len(set(ids))==8 and ids.index(s1.id)>ids.index(ordinary[-1].id) and ids.index(unknown.id)==7

def test_explicit_sort_overrides_default_regional_grouping():
 r1=Region.objects.create(code='1',name='منطقه ۱');r2=Region.objects.create(code='2',name='منطقه ۲');special=Center.objects.create(name='خاص',region=r1,is_special=True);regular=Center.objects.create(name='عادی',region=r2)
 make_space('1',r1,special);make_space('10',r2,regular);make_space('2',r2,regular)
 assert list(filter_spaces(params()).values_list('code',flat=True))==['2','10','1']
 assert list(filter_spaces(params(sort=['code'])).values_list('code',flat=True))==['1','2','10']

def test_mother_property_default_region_name_identifier_and_explicit_override():
 r1=Region.objects.create(code='1',name='منطقه ۱');r2=Region.objects.create(code='2',name='منطقه ۲')
 MotherProperty.objects.create(identifier='P-2',name='ب',region=r1,source_row=2);MotherProperty.objects.create(identifier='P-1',name='الف',region=r2,source_row=3);MotherProperty.objects.create(identifier='P-3',name='الف',region=r1,source_row=4)
 assert list(filter_mother_properties(params()).values_list('identifier',flat=True))==['P-3','P-2','P-1']
 assert list(filter_mother_properties(params(sort=['identifier'])).values_list('identifier',flat=True))==['P-1','P-2','P-3']

def test_saved_report_distinguishes_domain_default_from_explicit_sort():
 from django.contrib.auth import get_user_model
 from services.reports import save_report
 user=get_user_model().objects.create_user('reports')
 default=save_report(owner=user,name='پیش‌فرض',data=params(field=['code','name']))
 explicit=save_report(owner=user,name='کد عددی',data=params(field=['code','name'],sort=['code']))
 assert default.sorting==[] and 'sort' not in default.filters
 assert explicit.sorting==['code'] and explicit.filters['sort']==['code']
