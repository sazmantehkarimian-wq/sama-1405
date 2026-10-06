from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from domains.commission.models import CommissionMember, CommissionSession
from domains.identity.models import AuditEvent
from services.dates import normalize_jalali


@login_required
def members(request):
    return render(request, 'commission/members.html', {
        'members': CommissionMember.objects.all(),
        'roles': CommissionMember.Role.choices,
    })


@login_required
@require_POST
def member_create(request):
    full_name = request.POST.get('full_name', '').strip()
    position = request.POST.get('position', '').strip()
    role = request.POST.get('role', CommissionMember.Role.MEMBER)
    if not full_name or not position or role not in CommissionMember.Role.values:
        messages.error(request, 'نام، سمت و نقش معتبر عضو الزامی است.')
        return redirect('commission-members')
    start = request.POST.get('membership_start', '').strip()
    if start:
        try:
            start = normalize_jalali(start)
        except ValueError:
            messages.error(request, 'تاریخ شروع عضویت معتبر نیست.')
            return redirect('commission-members')
    with transaction.atomic():
        member = CommissionMember.objects.create(
            full_name=full_name,
            position=position,
            role=role,
            signature_order=request.POST.get('signature_order') or None,
            membership_start=start,
            notes=request.POST.get('notes', '').strip(),
        )
        AuditEvent.objects.create(
            actor=request.user, action='COMMISSION_MEMBER_CREATE', entity_type='CommissionMember',
            entity_id=str(member.pk), after={'full_name': member.full_name, 'position': member.position, 'role': member.role},
            ip_address=request.META.get('REMOTE_ADDR'),
        )
    messages.success(request, 'عضو مرجع کمیسیون ثبت شد.')
    return redirect('commission-members')


@login_required
@require_POST
def member_toggle(request, member_id):
    member = get_object_or_404(CommissionMember, pk=member_id)
    before = member.is_active
    member.is_active = not before
    member.save(update_fields=['is_active'])
    AuditEvent.objects.create(
        actor=request.user, action='COMMISSION_MEMBER_STATUS_CHANGE', entity_type='CommissionMember', entity_id=str(member.pk),
        before={'is_active': before}, after={'is_active': member.is_active}, ip_address=request.META.get('REMOTE_ADDR'),
    )
    messages.success(request, 'وضعیت عضو مرجع تغییر کرد؛ Snapshot جلسات قبلی بدون تغییر باقی ماند.')
    return redirect('commission-members')


@login_required
@require_POST
def session_transition(request, session_id):
    session = get_object_or_404(CommissionSession, pk=session_id)
    new_state = request.POST.get('state', '')
    allowed = {
        CommissionSession.State.DRAFT: {CommissionSession.State.PLANNED, CommissionSession.State.CANCELLED},
        CommissionSession.State.PLANNED: {CommissionSession.State.HELD, CommissionSession.State.CANCELLED},
        CommissionSession.State.HELD: {CommissionSession.State.FINALIZED},
        CommissionSession.State.FINALIZED: set(),
        CommissionSession.State.CANCELLED: set(),
    }
    if new_state not in allowed.get(session.state, set()):
        messages.error(request, 'این تغییر وضعیت برای جلسه مجاز نیست.')
        return redirect('commission-session-detail', session_id=session.pk)
    if new_state == CommissionSession.State.FINALIZED:
        if not session.cases.exists():
            messages.error(request, 'جلسه بدون موضوع قابل نهایی‌سازی نیست.')
            return redirect('commission-session-detail', session_id=session.pk)
        if session.cases.filter(decisions__isnull=True).exists():
            messages.error(request, 'برای نهایی‌سازی، همه موضوعات باید حداقل یک مصوبه ثبت‌شده داشته باشند.')
            return redirect('commission-session-detail', session_id=session.pk)
    before = session.state
    session.state = new_state
    if new_state == CommissionSession.State.FINALIZED:
        session.finalized_at = timezone.now()
        session.save(update_fields=['state', 'finalized_at'])
    else:
        session.save(update_fields=['state'])
    AuditEvent.objects.create(
        actor=request.user, action='COMMISSION_SESSION_STATE_CHANGE', entity_type='CommissionSession', entity_id=str(session.pk),
        reason=request.POST.get('reason', '').strip(), before={'state': before}, after={'state': new_state},
        ip_address=request.META.get('REMOTE_ADDR'),
    )
    messages.success(request, 'وضعیت جلسه با ثبت سابقه ممیزی تغییر کرد.')
    return redirect('commission-session-detail', session_id=session.pk)
