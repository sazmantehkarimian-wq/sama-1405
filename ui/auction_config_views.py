from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from domains.auctionflow.models import AuctionOrganizationProfile, AuctionTemplateSource
from services.auction_templates import REFERENCE_FILES, REFERENCE_VERSION


@login_required
def auction_configuration(request):
    organization=AuctionOrganizationProfile.objects.first()
    templates=AuctionTemplateSource.objects.select_related('source_document').order_by('family','kind','-imported_at')
    active={(item.family,item.kind):item for item in templates if item.active}
    expected=[]
    for filename,(family,kind,sha256) in REFERENCE_FILES.items():
        expected.append({
            'filename':filename,'family':family,'kind':kind,'sha256':sha256,
            'registered':active.get((family,kind)),
        })
    return render(request,'ui/auction_configuration.html',{
        'organization':organization,
        'templates':templates,
        'expected_templates':expected,
        'reference_version':REFERENCE_VERSION,
    })
