from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect

from domains.auctionflow.models import (
    AuctionDocumentInstance, AuctionLotProfile, AuctionOrganizationProfile,
    AuctionPeriodProfile, AuctionTemplateSource,
)
from domains.contracts.models import Beneficiary
from domains.operations.models import AuctionLot, AuctionPeriod, AuctionProposal
from services.auction_flow import generate_controlled_document, select_winner, start_contract_from_award
from services.auction_templates import import_reference_pack
from services.dates import normalize_jalali


def _ip(request):
    return request.META.get('REMOTE_ADDR')


def _date(value, label, required=False):
    value=(value or '').strip()
    if not value and not required:
        return ''
    if not value:
        raise ValidationError(f'{label} الزامی است.')
    try:
        return normalize_jalali(value)
    except ValueError as exc:
        raise ValidationError(f'{label} معتبر نیست.') from exc


def _money(value, label, required=False):
    value=(value or '').replace(',','').strip()
    if not value and not required:
        return None
    try:
        amount=Decimal(value)
    except (InvalidOperation, ValueError):
        raise ValidationError(f'{label} باید عدد معتبر باشد.')
    if amount < 0:
        raise ValidationError(f'{label} نمی‌تواند منفی باشد.')
    return amount


@login_required
@transaction.atomic
def organization_profile_save(request):
    if request.method != 'POST':
        return redirect('auction-workspace')
    profile=AuctionOrganizationProfile.objects.first() or AuctionOrganizationProfile()
    fields=[
        'organization_name','unit_title','official_address','secretariat_address','phone','bank_name','bank_branch',
        'account_number','iban','office_hours','submission_location','representative_name','representative_title',
        'economic_code','national_id','postal_code',
    ]
    for field in fields:
        setattr(profile,field,(request.POST.get(field) or '').strip())
    profile.organization_name=profile.organization_name or 'سازمان فرهنگی هنری شهرداری تهران'
    profile.unit_title=profile.unit_title or 'مدیریت اقتصادی و املاک — اداره املاک و مستغلات'
    profile.updated_by=request.user
    profile.save()
    messages.success(request,'مشخصات ثابت سازمان برای اسناد مزایده ذخیره شد.')
    return redirect('auction-workspace')


@login_required
@transaction.atomic
def template_pack_import(request):
    if request.method != 'POST':
        return redirect('auction-workspace')
    uploaded=request.FILES.get('template_pack')
    if not uploaded:
        messages.error(request,'فایل ZIP بسته قالب‌های مرجع را انتخاب کنید.')
        return redirect('auction-workspace')
    try:
        created=import_reference_pack(uploaded=uploaded,actor=request.user,ip_address=_ip(request))
    except ValidationError as exc:
        messages.error(request,' '.join(exc.messages))
    else:
        messages.success(request,f'بسته قالب‌های مرجع با کنترل SHA ثبت شد؛ {len(created)} Master Source معتبر شناسایی شد. وضعیت فعلی UAT Reference است و تا تأیید چاپی Golden Master نهایی نیست.')
    return redirect('auction-workspace')


@login_required
@transaction.atomic
def period_profile_save(request, period_id):
    period=get_object_or_404(AuctionPeriod,pk=period_id)
    if request.method!='POST':
        return redirect('auction-period-detail',period_id=period.pk)
    try:
        duration=int(request.POST.get('duration_years') or 1)
        if duration < 1 or duration > 20:
            raise ValidationError('مدت واگذاری باید بین ۱ تا ۲۰ سال باشد.')
        profile,_=AuctionPeriodProfile.objects.get_or_create(period=period)
        profile.permit_reference=request.POST.get('permit_reference','').strip()
        profile.permit_date=_date(request.POST.get('permit_date'),'تاریخ مجوز')
        profile.ad_day_name=request.POST.get('ad_day_name','').strip()
        profile.ad_date=_date(request.POST.get('ad_date'),'تاریخ درج آگهی')
        profile.newspaper=request.POST.get('newspaper','').strip() or 'همشهری'
        profile.newspaper_page=request.POST.get('newspaper_page','').strip()
        profile.publication_media=request.POST.get('publication_media','').strip()
        profile.document_sales_start=_date(request.POST.get('document_sales_start'),'شروع فروش اسناد')
        profile.document_sales_end=_date(request.POST.get('document_sales_end'),'پایان فروش اسناد')
        profile.proposal_deadline=_date(request.POST.get('proposal_deadline'),'آخرین مهلت تحویل پیشنهاد')
        profile.submission_day_name=request.POST.get('submission_day_name','').strip()
        profile.invitation_number=request.POST.get('invitation_number','').strip()
        profile.invitation_date=_date(request.POST.get('invitation_date'),'تاریخ دعوتنامه')
        profile.opening_session_date=_date(request.POST.get('opening_session_date'),'تاریخ جلسه بازگشایی')
        profile.opening_day_name=request.POST.get('opening_day_name','').strip()
        profile.opening_session_time=request.POST.get('opening_session_time','').strip()
        profile.opening_session_location=request.POST.get('opening_session_location','').strip()
        profile.duration_years=duration
        profile.notes=request.POST.get('notes','').strip()
        profile.updated_by=request.user
        profile.save()
    except ValidationError as exc:
        messages.error(request,' '.join(exc.messages))
    else:
        messages.success(request,'اطلاعات اجرایی دوره مزایده ثبت شد و منبع واحد AUC-* به‌روزرسانی شد.')
    return redirect('auction-period-detail',period_id=period.pk)


@login_required
@transaction.atomic
def lot_profile_save(request, lot_id):
    lot=get_object_or_404(AuctionLot.objects.select_related('period','space'),pk=lot_id)
    if request.method!='POST':
        return redirect('auction-period-detail',period_id=lot.period_id)
    try:
        family=request.POST.get('template_family','COMMERCIAL')
        if family not in AuctionLotProfile.Family.values:
            raise ValidationError('خانواده قالب معتبر نیست.')
        profile,_=AuctionLotProfile.objects.get_or_create(lot=lot)
        profile.template_family=family
        profile.base_monthly_rent_rial=_money(request.POST.get('base_monthly_rent_rial'),'اجاره پایه ماهانه')
        profile.base_monthly_rent_words=request.POST.get('base_monthly_rent_words','').strip()
        profile.guarantee_amount_rial=_money(request.POST.get('guarantee_amount_rial'),'تضمین شرکت در مزایده')
        profile.guarantee_type=request.POST.get('guarantee_type','').strip()
        profile.grace_period=request.POST.get('grace_period','').strip()
        profile.investment_amount_rial=_money(request.POST.get('investment_amount_rial'),'مبلغ سرمایه‌گذاری')
        profile.investment_description=request.POST.get('investment_description','').strip()
        profile.proposed_job=request.POST.get('proposed_job','').strip()
        profile.transaction_level=request.POST.get('transaction_level','').strip()
        profile.location_description=request.POST.get('location_description','').strip()
        profile.coordination_phone=request.POST.get('coordination_phone','').strip()
        profile.coordination_person=request.POST.get('coordination_person','').strip()
        profile.save()
    except ValidationError as exc:
        messages.error(request,' '.join(exc.messages))
    else:
        messages.success(request,f'اطلاعات ردیف مزایده فضای {lot.space.code} و منبع LOT-* ثبت شد.')
    return redirect('auction-period-detail',period_id=lot.period_id)


@login_required
@transaction.atomic
def winner_select(request, lot_id):
    lot=get_object_or_404(AuctionLot.objects.select_related('period','space'),pk=lot_id)
    if request.method!='POST':
        return redirect('auction-period-detail',period_id=lot.period_id)
    try:
        winner_id=request.POST.get('winner_proposal_id','').strip()
        if not winner_id.isdigit():
            raise ValidationError('پیشنهاد برنده را انتخاب کنید.')
        winner=get_object_or_404(AuctionProposal.objects.select_related('participant'),pk=int(winner_id))
        runner_id=request.POST.get('runner_up_proposal_id','').strip()
        runner=get_object_or_404(AuctionProposal.objects.select_related('participant'),pk=int(runner_id)) if runner_id.isdigit() else None
        profile=select_winner(
            lot=lot,winner_proposal=winner,runner_up_proposal=runner,
            decision_reference=request.POST.get('decision_reference',''),
            decision_date=_date(request.POST.get('decision_date'),'تاریخ تصمیم کمیسیون',required=True),
            actor=request.user,ip_address=_ip(request),
        )
    except ValidationError as exc:
        messages.error(request,' '.join(exc.messages))
    else:
        messages.success(request,f'برنده فضای {lot.space.code} ثبت شد: {profile.winner_proposal.participant.name}. انتخاب برنده توسط کاربر ثبت شده و خودکار نبوده است.')
    return redirect('auction-period-detail',period_id=lot.period_id)


@login_required
@transaction.atomic
def contract_start(request, lot_id):
    lot=get_object_or_404(AuctionLot.objects.select_related('period','space'),pk=lot_id)
    if request.method!='POST':
        return redirect('auction-period-detail',period_id=lot.period_id)
    kind=request.POST.get('beneficiary_kind',Beneficiary.Kind.NATURAL)
    if kind not in Beneficiary.Kind.values:
        kind=Beneficiary.Kind.NATURAL
    try:
        circulation=start_contract_from_award(
            lot=lot,actor=request.user,beneficiary_kind=kind,
            operational_start_date=_date(request.POST.get('operational_start_date'),'تاریخ شروع فرایند قرارداد',required=True),
            due_date=_date(request.POST.get('due_date'),'مهلت اقدام'),ip_address=_ip(request),
        )
    except ValidationError as exc:
        messages.error(request,' '.join(exc.messages))
        return redirect('auction-period-detail',period_id=lot.period_id)
    messages.success(request,f'گردش قرارداد {circulation.identity} از نتیجه مزایده ایجاد شد. ادامه کار از پرونده قرارداد انجام می‌شود.')
    return redirect('contract-circulation-detail',pk=circulation.pk)


@login_required
@transaction.atomic
def document_generate(request, lot_id, document_type):
    lot=get_object_or_404(AuctionLot.objects.select_related('period','space'),pk=lot_id)
    if request.method!='POST':
        return redirect('auction-period-detail',period_id=lot.period_id)
    if document_type not in AuctionDocumentInstance.DocumentType.values:
        messages.error(request,'نوع سند درخواستی معتبر نیست.')
        return redirect('auction-period-detail',period_id=lot.period_id)
    try:
        instance=generate_controlled_document(lot=lot,document_type=document_type,actor=request.user,ip_address=_ip(request))
    except ValidationError as exc:
        messages.error(request,' '.join(exc.messages))
    else:
        messages.success(request,f'{instance.get_document_type_display()} از Master Source قفل‌شده تولید شد. تا تأیید چاپی مالک، وضعیت خروجی UAT_DRAFT باقی می‌ماند.')
    return redirect('auction-period-detail',period_id=lot.period_id)
