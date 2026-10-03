import re
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import get_object_or_404, render

from domains.properties.models import Region, Center, MotherProperty, CommercialSpace
from domains.contracts.models import Contract
from domains.operations.models import Appraisal, Auction, CommissionDecision, WorkflowInstance, Alert
from domains.documents.models import Document


def _num(value):
    text = str(value or '').translate(str.maketrans('۰۱۲۳۴۵۶۷۸۹','0123456789'))
    match = re.search(r'\d+', text)
    return int(match.group()) if match else 999


def _ordered_regions():
    return sorted(Region.objects.all(), key=lambda r: (_num(r.code), _num(r.name), r.name))


def _region_context(region):
    spaces = CommercialSpace.objects.filter(region=region)
    active = spaces.filter(status=CommercialSpace.Status.ACTIVE)
    mothers = MotherProperty.objects.filter(region=region)
    return {
        'space_total': spaces.count(),
        'active_count': active.count(),
        'out_count': spaces.filter(status=CommercialSpace.Status.OUT_OF_CYCLE).count(),
        'mother_count': mothers.count(),
        'without_contract_count': active.filter(contracts__isnull=True).distinct().count(),
        'without_appraisal_count': active.filter(appraisals__isnull=True).distinct().count(),
        'contract_count': Contract.objects.filter(space__region=region).count(),
        'appraisal_count': Appraisal.objects.filter(space__region=region).count(),
        'auction_count': Auction.objects.filter(space__region=region).count(),
        'workflow_count': WorkflowInstance.objects.filter(space__region=region, state='OPEN').count(),
        'alert_count': Alert.objects.filter(space__region=region).exclude(status='RESOLVED').count(),
        'mother_properties': mothers.order_by('name')[:12],
        'spaces': spaces.select_related('center').order_by('center__name','code')[:20],
    }


@login_required
def regions_workspace(request):
    regions = _ordered_regions()
    return render(request, 'ui/regions_workspace.html', {
        'regions': regions,
        'special_centers': Center.objects.filter(is_special=True).select_related('region').order_by('region__name','name'),
    })


@login_required
def region_detail(request, code):
    region = get_object_or_404(Region, code=code)
    context = {'regions': _ordered_regions(), 'region': region}
    context.update(_region_context(region))
    return render(request, 'ui/regions_workspace.html', context)


@login_required
def special_centers(request):
    centers = Center.objects.filter(is_special=True).select_related('region').annotate(space_total=Count('commercialspace')).order_by('region__name','name')
    return render(request, 'ui/regions_workspace.html', {'regions': _ordered_regions(), 'special_centers': centers, 'special_mode': True})


@login_required
def special_center_detail(request, center_id):
    center = get_object_or_404(Center.objects.select_related('region'), pk=center_id, is_special=True)
    spaces = CommercialSpace.objects.filter(center=center)
    active = spaces.filter(status=CommercialSpace.Status.ACTIVE)
    mother_ids = spaces.values_list('property_links__mother_property_id', flat=True)
    mothers = MotherProperty.objects.filter(pk__in=mother_ids).distinct()
    return render(request, 'ui/regions_workspace.html', {
        'regions': _ordered_regions(),
        'special_mode': True,
        'special_center': center,
        'special_centers': Center.objects.filter(is_special=True).select_related('region').order_by('region__name','name'),
        'space_total': spaces.count(),
        'active_count': active.count(),
        'out_count': spaces.filter(status=CommercialSpace.Status.OUT_OF_CYCLE).count(),
        'mother_count': mothers.count(),
        'without_contract_count': active.filter(contracts__isnull=True).distinct().count(),
        'without_appraisal_count': active.filter(appraisals__isnull=True).distinct().count(),
        'contract_count': Contract.objects.filter(space__center=center).count(),
        'appraisal_count': Appraisal.objects.filter(space__center=center).count(),
        'auction_count': Auction.objects.filter(space__center=center).count(),
        'workflow_count': WorkflowInstance.objects.filter(space__center=center, state='OPEN').count(),
        'alert_count': Alert.objects.filter(space__center=center).exclude(status='RESOLVED').count(),
        'mother_properties': mothers.order_by('name')[:12],
        'spaces': spaces.order_by('code')[:20],
    })
