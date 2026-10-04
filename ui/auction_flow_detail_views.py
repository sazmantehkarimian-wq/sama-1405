from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

from domains.auctionflow.models import AuctionDocumentInstance
from domains.documents.models import Document
from domains.operations.models import AuctionPeriod
from services.auction_flow import ensure_profiles, sync_official_contract


@login_required
def auction_period_detail(request, period_id):
    period=get_object_or_404(
        AuctionPeriod.objects.prefetch_related(
            'lots__space','lots__proposals__participant','participants','generated_documents__document'
        ),pk=period_id,
    )
    period_profile, lot_profiles=ensure_profiles(period)
    for profile in lot_profiles:
        if profile.contract_circulation_id:
            sync_official_contract(circulation=profile.contract_circulation)
    documents=Document.objects.filter(
        entity_type='AuctionPeriod',entity_id=str(period.pk),archived_at__isnull=True
    ).order_by('-uploaded_at','-pk')
    generated=AuctionDocumentInstance.objects.filter(period=period).select_related('lot__space','document','generated_by').order_by('-generated_at','-pk')
    return render(request,'ui/auction_period_detail.html',{
        'period':period,
        'period_profile':period_profile,
        'documents':documents,
        'generated_documents':generated,
        'document_types':AuctionDocumentInstance.DocumentType.choices,
    })
