import pytest
from django.contrib.auth import get_user_model

from domains.operations.models import Alert, WorkflowInstance
from domains.properties.models import CommercialSpace, Region


@pytest.mark.django_db
def test_dashboard_scope_uses_same_space_dataset_as_drilldown(client):
    user=get_user_model().objects.create_user('dashboard-scope',password='A-very-safe-password')
    client.force_login(user)
    r1=Region.objects.create(code='1',name='منطقه ۱')
    r2=Region.objects.create(code='2',name='منطقه ۲')
    CommercialSpace.objects.create(code='9101',name='فعال منطقه یک',status='ACTIVE',region=r1,current_usage='فرهنگی')
    CommercialSpace.objects.create(code='9102',name='خارج منطقه یک',status='OUT_OF_CYCLE',region=r1,current_usage='فرهنگی')
    CommercialSpace.objects.create(code='9201',name='فعال منطقه دو',status='ACTIVE',region=r2,current_usage='ورزشی')

    dashboard=client.get('/',{'region_id':str(r1.pk)})
    assert dashboard.status_code==200
    assert dashboard.context['scope_count']==2
    assert dashboard.context['active_count']==1
    assert dashboard.context['inactive_count']==1
    assert 'مناطق: منطقه ۱' in dashboard.context['scope_summary']

    active=client.get('/spaces/',{'region_id':str(r1.pk),'status':'ACTIVE'})
    assert active.status_code==200
    assert active.context['total']==dashboard.context['active_count']==1

    inactive=client.get('/spaces/',{'region_id':str(r1.pk),'status':'OUT_OF_CYCLE'})
    assert inactive.context['total']==dashboard.context['inactive_count']==1


@pytest.mark.django_db
def test_dashboard_action_center_is_scoped_to_visible_spaces(client):
    user=get_user_model().objects.create_user('dashboard-action',password='A-very-safe-password')
    client.force_login(user)
    r1=Region.objects.create(code='3',name='منطقه ۳')
    r2=Region.objects.create(code='4',name='منطقه ۴')
    s1=CommercialSpace.objects.create(code='9301',name='فضای یک',status='ACTIVE',region=r1)
    s2=CommercialSpace.objects.create(code='9401',name='فضای دو',status='ACTIVE',region=r2)

    Alert.objects.create(space=s1,subject='بحرانی',reason='پیگیری',priority='CRITICAL',status='OPEN',due_date='1405/01/01',target_url='/spaces/9301/')
    Alert.objects.create(space=s2,subject='خارج از دامنه',reason='پیگیری',priority='HIGH',status='OPEN',target_url='/spaces/9401/')
    WorkflowInstance.objects.create(space=s1,process_type='FILE',title='پرونده باز',state='OPEN',next_action='پیگیری',due_date='1405/01/01',created_by=user)
    WorkflowInstance.objects.create(space=s2,process_type='FILE',title='خارج دامنه',state='OPEN',next_action='پیگیری',due_date='1405/01/01',created_by=user)

    response=client.get('/',{'region_id':str(r1.pk)})
    assert response.status_code==200
    assert response.context['alert_count']==1
    assert response.context['critical_alert_count']==1
    assert response.context['high_alert_count']==0
    assert response.context['open_workflow_count']==1
    assert response.context['overdue_workflow_count']==1

    alerts=client.get('/actions/',{'region_id':str(r1.pk),'kind':'alerts'})
    assert alerts.status_code==200
    assert alerts.context['alert_count']==response.context['alert_count']==1
    assert alerts.context['workflow_count']==0
    assert '9301' in alerts.content.decode()
    assert '9401' not in alerts.content.decode()

    workflows=client.get('/actions/',{'region_id':str(r1.pk),'kind':'workflows','overdue':'1'})
    assert workflows.status_code==200
    assert workflows.context['workflow_count']==response.context['overdue_workflow_count']==1
    assert workflows.context['alert_count']==0


@pytest.mark.django_db
def test_action_center_priority_drilldown_matches_dashboard_kpi(client):
    user=get_user_model().objects.create_user('dashboard-priority',password='A-very-safe-password')
    client.force_login(user)
    region=Region.objects.create(code='5',name='منطقه ۵')
    space=CommercialSpace.objects.create(code='9601',name='فضای اقدام',status='ACTIVE',region=region)
    Alert.objects.create(space=space,subject='بحرانی',reason='اقدام',priority='CRITICAL',status='OPEN',target_url='/spaces/9601/')
    Alert.objects.create(space=space,subject='متوسط',reason='اقدام',priority='MEDIUM',status='OPEN',target_url='/spaces/9601/')

    dashboard=client.get('/',{'region_id':str(region.pk)})
    critical=client.get('/actions/',{'region_id':str(region.pk),'kind':'alerts','priority':'CRITICAL'})
    assert critical.status_code==200
    assert critical.context['alert_count']==dashboard.context['critical_alert_count']==1
    body=critical.content.decode()
    assert 'بحرانی' in body
    assert 'متوسط' not in body


@pytest.mark.django_db
def test_dashboard_usage_scope_is_explicit_and_resettable(client):
    user=get_user_model().objects.create_user('dashboard-usage',password='A-very-safe-password')
    client.force_login(user)
    CommercialSpace.objects.create(code='9501',name='ورزشی',status='ACTIVE',current_usage='ورزشی')
    CommercialSpace.objects.create(code='9502',name='فرهنگی',status='ACTIVE',current_usage='فرهنگی')

    response=client.get('/',{'usage':'ورزشی'})
    assert response.status_code==200
    assert response.context['scope_count']==1
    assert response.context['active_count']==1
    assert 'کاربری: ورزشی' in response.context['scope_summary']
    body=response.content.decode()
    assert 'بازگشت به کل سازمان' in body
    assert 'ورزشی' in body
