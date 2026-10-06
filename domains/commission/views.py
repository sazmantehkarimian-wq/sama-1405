from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from domains.commission.models import (
    CommissionCase,
    CommissionDecision,
    CommissionFollowUp,
    CommissionMember,
    CommissionSession,
)
from domains.contracts.models import Beneficiary, Contract
from domains.documents.models import Document
from domains.operations.models import AuctionPeriod, CommissionDecision as LegacyCommissionDecision
from domains.properties.models import CommercialSpace, MotherProperty
from services.commission import add_case, add_decision, add_follow_up, complete_follow_up, create_session


@login_required
def workspace(request):
    q = request.GET.get('q', '').strip()
    state = request.GET.get('state', '').strip()
    sessions = CommissionSession.objects.annotate(
        case_count=Count('cases', distinct=True),
        open_decision_count=Count('cases__decisions', filter=~Q(cases__decisions__execution_state='DONE'), distinct=True),
    ).select_related('created_by')
    if q:
        sessions = sessions.filter(Q(internal_code__icontains=q) | Q(session_number__icontains=q) | Q(title__icontains=q))
    if state:
        sessions = sessions.filter(state=state)
    context = {
        'sessions': sessions[:100],
        'states': CommissionSession.State.choices,
        'q': q,
        'selected_state': state,
        'open_followups': CommissionFollowUp.objects.exclude(state__in=['DONE', 'CANCELLED']).select_related('decision__case__session')[:20],
        'legacy_decisions': LegacyCommissionDecision.objects.prefetch_related('spaces').order_by('-id')[:20],
        'legacy_count': LegacyCommissionDecision.objects.count(),
        'kpi_sessions': CommissionSession.objects.count(),
        'kpi_cases': CommissionCase.objects.count(),
        'kpi_open': CommissionDecision.objects.exclude(execution_state__in=['DONE', 'CANCELLED']).count(),
    }
    return render(request, 'commission/workspace.html', context)


@login_required
def session_create_page(request):
    return render(request, 'commission/session_form.html', {'members': CommissionMember.objects.filter(is_active=True)})


@login_required
@require_POST
def session_create(request):
    selected = CommissionMember.objects.filter(pk__in=request.POST.getlist('members'), is_active=True)
    try:
        session = create_session(actor=request.user, values=request.POST, members=selected, ip_address=request.META.get('REMOTE_ADDR'))
    except ValidationError as exc:
        messages.error(request, ' '.join(exc.messages))
        return redirect('commission-session-new')
    messages.success(request, f'جلسه {session.internal_code} ایجاد شد.')
    return redirect('commission-session-detail', session_id=session.pk)


@login_required
def session_detail(request, session_id):
    session = get_object_or_404(
        CommissionSession.objects.select_related('created_by').prefetch_related(
            'session_members', 'cases__related_entities__space', 'cases__related_entities__contract',
            'cases__related_entities__beneficiary', 'cases__related_entities__auction_period',
            'cases__related_entities__mother_property', 'cases__decisions__follow_ups',
        ), pk=session_id,
    )
    return render(request, 'commission/session_detail.html', {
        'session': session,
        'spaces': CommercialSpace.objects.order_by('code'),
        'contracts': Contract.objects.select_related('space', 'beneficiary').order_by('-id')[:1000],
        'beneficiaries': Beneficiary.objects.filter(archived_at__isnull=True).order_by('name')[:1000],
        'auction_periods': AuctionPeriod.objects.order_by('-id')[:200],
        'mother_properties': MotherProperty.objects.order_by('name')[:1000],
    })


@login_required
@require_POST
def case_create(request, session_id):
    session = get_object_or_404(CommissionSession, pk=session_id)
    related_space = CommercialSpace.objects.filter(code=request.POST.get('space_code')).first() if request.POST.get('space_code') else None
    related_contract = Contract.objects.filter(pk=request.POST.get('contract_id')).first() if request.POST.get('contract_id') else None
    related_beneficiary = Beneficiary.objects.filter(pk=request.POST.get('beneficiary_id')).first() if request.POST.get('beneficiary_id') else None
    related_auction_period = AuctionPeriod.objects.filter(pk=request.POST.get('auction_period_id')).first() if request.POST.get('auction_period_id') else None
    related_mother_property = MotherProperty.objects.filter(pk=request.POST.get('mother_property_id')).first() if request.POST.get('mother_property_id') else None
    try:
        case = add_case(
            session=session, actor=request.user, values=request.POST, related_space=related_space,
            related_contract=related_contract, related_beneficiary=related_beneficiary,
            related_auction_period=related_auction_period, related_mother_property=related_mother_property,
            ip_address=request.META.get('REMOTE_ADDR'),
        )
    except ValidationError as exc:
        messages.error(request, ' '.join(exc.messages))
        return redirect('commission-session-detail', session_id=session.pk)
    messages.success(request, f'موضوع {case.internal_code} به دستور جلسه افزوده شد.')
    return redirect('commission-case-detail', case_id=case.pk)


@login_required
def case_detail(request, case_id):
    case = get_object_or_404(
        CommissionCase.objects.select_related('session', 'created_by').prefetch_related(
            'related_entities__space', 'related_entities__contract__space', 'related_entities__beneficiary',
            'related_entities__auction_period', 'related_entities__mother_property', 'decisions__follow_ups'
        ), pk=case_id,
    )
    space_ids = [r.space.code for r in case.related_entities.all() if r.space_id]
    documents = Document.objects.filter(archived_at__isnull=True).filter(
        Q(entity_type='CommercialSpace', entity_id__in=space_ids) |
        Q(entity_type='CommissionCase', entity_id=str(case.pk))
    ).order_by('-uploaded_at')[:100]
    return render(request, 'commission/case_detail.html', {'case': case, 'documents': documents})


@login_required
@require_POST
def decision_create(request, case_id):
    case = get_object_or_404(CommissionCase.objects.select_related('session'), pk=case_id)
    document = None
    if request.POST.get('document_id'):
        document = get_object_or_404(Document, pk=request.POST['document_id'], archived_at__isnull=True)
    try:
        decision = add_decision(case=case, actor=request.user, values=request.POST, document=document, ip_address=request.META.get('REMOTE_ADDR'))
    except ValidationError as exc:
        messages.error(request, ' '.join(exc.messages))
    else:
        messages.success(request, f'مصوبه {decision.internal_code} ثبت و در پرونده‌های مرتبط منعکس شد.')
    return redirect('commission-case-detail', case_id=case.pk)


@login_required
@require_POST
def followup_create(request, decision_id):
    decision = get_object_or_404(CommissionDecision.objects.select_related('case'), pk=decision_id)
    try:
        add_follow_up(decision=decision, actor=request.user, values=request.POST, ip_address=request.META.get('REMOTE_ADDR'))
    except ValidationError as exc:
        messages.error(request, ' '.join(exc.messages))
    else:
        messages.success(request, 'اقدام پیگیری مصوبه ثبت شد.')
    return redirect('commission-case-detail', case_id=decision.case_id)


@login_required
@require_POST
def followup_complete(request, followup_id):
    followup = get_object_or_404(CommissionFollowUp.objects.select_related('decision__case'), pk=followup_id)
    try:
        complete_follow_up(follow_up=followup, actor=request.user, outcome=request.POST.get('outcome', ''), ip_address=request.META.get('REMOTE_ADDR'))
    except ValidationError as exc:
        messages.error(request, ' '.join(exc.messages))
    else:
        messages.success(request, 'پیگیری با ثبت نتیجه مختومه شد.')
    return redirect('commission-case-detail', case_id=followup.decision.case_id)
