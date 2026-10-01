from django.contrib.auth.decorators import login_required,user_passes_test
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import render,get_object_or_404,redirect
from django.db.models import Count
from domains.properties.models import CommercialSpace,Region,Center,MotherProperty
from domains.registry.models import Discrepancy
from domains.identity.models import UserProfile, SavedFilter, SavedReport, ArchivedReportSnapshot
from domains.contracts.models import Contract, Beneficiary
from domains.operations.models import Appraisal, AppraisalFee, Auction, AuctionEvaluation, AuctionPeriod, AuctionRule, CommissionDecision, UtilityRecord, UtilityObligation, FileMovement, WorkflowInstance, Alert, DecisionOrder
from domains.documents.models import Document
from queries.spaces import filter_spaces
from services.file_movement import current_holder
from reporting.engine import excel,docx,pdf,tabular_excel
from ui.forms import PersianPasswordChangeForm
@login_required
def dashboard(request):
 spaces=CommercialSpace.objects.all();active=spaces.filter(status='ACTIVE')
 region_rows=list(active.exclude(region=None).values('region__name').annotate(total=Count('id')).order_by('-total')[:5]);maximum=max((row['total'] for row in region_rows),default=1)
 for row in region_rows:row['percent']=round(row['total']*100/maximum)
 context={'space_count':spaces.count(),'active_count':active.count(),'inactive_count':spaces.filter(status='OUT_OF_CYCLE').count(),'property_count':MotherProperty.objects.count(),'discrepancy_count':Discrepancy.objects.exclude(status='RESOLVED').count(),'contract_count':Contract.objects.count(),'appraisal_count':Appraisal.objects.count(),'alert_count':Alert.objects.exclude(status='RESOLVED').count(),'without_contract_count':active.filter(contracts__isnull=True).count(),'without_appraisal_count':active.filter(appraisals__isnull=True).count(),'open_workflow_count':WorkflowInstance.objects.filter(state='OPEN').count(),'region_rows':region_rows}
 return render(request,'ui/dashboard.html',context)
@login_required
def space_list(request):
 qs=filter_spaces(request.GET);page=Paginator(qs,25).get_page(request.GET.get('page'))
 allowed_columns={'name','status','region','usage','area'}
 requested=set(request.GET.getlist('column')) & allowed_columns
 visible=requested or allowed_columns
 return render(request,'ui/space_list.html',{'page':page,'regions':Region.objects.all(),'centers':Center.objects.filter(is_special=True),'total':qs.count(),'saved_filters':SavedFilter.objects.filter(owner=request.user,domain='spaces'),'visible_columns':visible})
@login_required
def space_detail(request,code):
 s=get_object_or_404(CommercialSpace.objects.select_related('region','center').prefetch_related('status_history','contracts__amendments','beneficiary_assignments__beneficiary','appraisals','auctions','utilities','utility_obligations','decisions','commission_decisions','timeline','alerts','file_movements','workflows','source_documents','property_links__mother_property'),code=code)
 timeline=s.timeline.all();event_type=request.GET.get('event_type','').strip()
 if event_type:timeline=timeline.filter(event_type=event_type)
 event_types=s.timeline.order_by().values_list('event_type',flat=True).distinct()
 return render(request,'ui/space_detail.html',{'space':s,'holder':current_holder(s),'timeline_events':timeline,'event_types':event_types,'uploaded_documents':Document.objects.filter(entity_type='CommercialSpace',entity_id=s.code,archived_at__isnull=True),'history':__import__('domains.operations.models',fromlist=['OperationalHistory']).OperationalHistory.objects.filter(entity_type__in=['WorkflowInstance','AppraisalFee','UtilityRecord','CommissionDecision','Alert'])[:100]})

@login_required
@require_POST
def save_space_filter(request):
 from django.http import QueryDict
 name=request.POST.get('name','').strip()
 if not name:
  messages.error(request,'نام نمای ذخیره‌شده الزامی است.');return redirect('space-list')
 excluded={'csrfmiddlewaretoken','name'}
 definition={key:request.POST.getlist(key) for key in request.POST if key not in excluded and request.POST.getlist(key)}
 SavedFilter.objects.create(owner=request.user,name=name,domain='spaces',definition=definition)
 messages.success(request,'نمای فیلتر ذخیره شد.');return redirect('space-list')

@login_required
def open_space_filter(request,filter_id):
 from urllib.parse import urlencode
 saved=get_object_or_404(SavedFilter,pk=filter_id,owner=request.user,domain='spaces')
 pairs=[(key,value) for key,values in saved.definition.items() for value in values]
 return redirect('/spaces/?'+urlencode(pairs))

@login_required
@require_POST
def rename_space_filter(request,filter_id):
 saved=get_object_or_404(SavedFilter,pk=filter_id,owner=request.user,domain='spaces');name=request.POST.get('name','').strip()
 if name:saved.name=name;saved.save(update_fields=['name']);messages.success(request,'نام فیلتر ذخیره‌شده تغییر کرد.')
 return redirect('space-list')

@login_required
@require_POST
def delete_space_filter(request,filter_id):
 get_object_or_404(SavedFilter,pk=filter_id,owner=request.user,domain='spaces').delete();messages.success(request,'فیلتر ذخیره‌شده حذف شد.')
 return redirect('space-list')

DOMAIN_LISTS={
 'properties':('املاک مادر',MotherProperty.objects.select_related('region'),(('identifier','شناسه ملک'),('name','نام'),('region.name','منطقه'),('primary_usage','کاربری'),('area','مساحت'))),
 'discrepancies':('بررسی مغایرت‌های داده',Discrepancy.objects.select_related('source_file','assigned_to'),(('entity_key','شناسه رکورد'),('field_key','فیلد'),('observed_value','مقدار موجود'),('expected_value','مقدار مورد انتظار'),('reason','علت'),('severity','اهمیت'),('status','وضعیت'))),
 'contracts':('قراردادها',Contract.objects.select_related('space'),(('number','شماره'),('space.code','کد فضا'),('start_date','شروع'),('end_date','پایان'),('status','وضعیت'))),
 'beneficiaries':('بهره‌برداران',Beneficiary.objects.all(),(('name','نام'),('identity_number','شناسه'),('kind','نوع'),('contact','تماس'))),
 'appraisals':('کارشناسی',Appraisal.objects.select_related('space'),(('space.code','کد فضا'),('appraisal_date','تاریخ'),('appraiser','کارشناس'),('amount_rial','مبلغ (ریال)'),('status','وضعیت'))),
 'fees':('حق‌الزحمه کارشناسی',AppraisalFee.objects.select_related('appraisal__space'),(('appraisal.space.code','کد فضا'),('amount_rial','مبلغ (ریال)'),('payment_status','پرداخت'),('payment_date','تاریخ پرداخت'),('follow_up_date','پیگیری'))),
 'auctions':('مزایده‌ها',Auction.objects.select_related('space'),(('space.code','کد فضا'),('year','سال'),('sequence','نوبت'),('stage','مرحله'),('result','نتیجه'))),
 'commissions':('کمیسیون معاملات',CommissionDecision.objects.all(),(('identity','شناسه'),('decision_date','تاریخ'),('subject','موضوع'),('decision','تصمیم'))),
 'utilities':('انشعابات و مصرف',UtilityRecord.objects.select_related('space'),(('space.code','کد فضا'),('utility_type','نوع'),('account_number','اشتراک'),('bill_amount_rial','مبلغ قبض (ریال)'),('payment_status','پرداخت'))),
 'workflows':('گردش پرونده',WorkflowInstance.objects.select_related('space'),(('space.code','کد فضا'),('title','فرایند'),('state','وضعیت'),('next_action','اقدام بعدی'),('due_date','مهلت'))),
 'alerts':('هشدارها',Alert.objects.select_related('space'),(('space.code','کد فضا'),('subject','موضوع'),('reason','علت'),('due_date','سررسید'),('status','وضعیت'))),
 'documents':('اسناد بارگذاری‌شده',Document.objects.all(),(('title','عنوان'),('document_type','نوع'),('original_filename','نام فایل'),('uploaded_at','زمان بارگذاری'))),
}
def _value(obj,path):
 parts=path.split('.')
 for index,part in enumerate(parts):
  display=getattr(obj,f'get_{part}_display',None) if index==len(parts)-1 else None
  if display:return display()
  obj=getattr(obj,part,None)
  if obj is None:return '—'
 return obj if obj not in ('',None) else '—'
@login_required
def domain_list(request,domain):
 title,qs,columns=DOMAIN_LISTS[domain]
 q=request.GET.get('q','').strip()
 if q and domain=='contracts':qs=qs.filter(number__icontains=q)
 page=Paginator(qs.order_by('-pk'),30).get_page(request.GET.get('page'))
 rows=[{'object':obj,'values':[_value(obj,key) for key,_ in columns]} for obj in page]
 return render(request,'ui/domain_list.html',{'title':title,'headers':[label for _,label in columns],'rows':rows,'page':page,'domain':domain})

@login_required
def domain_excel(request,domain):
 if domain not in DOMAIN_LISTS:return HttpResponse(status=404)
 title,qs,columns=DOMAIN_LISTS[domain]
 q=request.GET.get('q','').strip()
 if q and domain=='contracts':qs=qs.filter(number__icontains=q)
 labels=[label for _,label in columns]
 data=([_value(item,key) for key,_ in columns] for item in qs.order_by('pk')[:10000])
 return HttpResponse(tabular_excel(title,labels,data),content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',headers={'Content-Disposition':f'attachment; filename="{domain}.xlsx"'})

@login_required
@require_POST
def discrepancy_review(request,discrepancy_id):
 item=get_object_or_404(Discrepancy,pk=discrepancy_id);status=request.POST.get('status','')
 if status not in Discrepancy.Status.values:
  messages.error(request,'وضعیت بررسی معتبر نیست.');return redirect('domain-list',domain='discrepancies')
 resolution=request.POST.get('resolution','').strip()
 if status==Discrepancy.Status.RESOLVED and not resolution:
  messages.error(request,'برای حل مغایرت، نتیجه بررسی را ثبت کنید.');return redirect('domain-list',domain='discrepancies')
 item.status=status;item.resolution=resolution;item.assigned_to=request.user;item.save(update_fields=['status','resolution','assigned_to']);messages.success(request,'وضعیت مغایرت ثبت شد.')
 return redirect('domain-list',domain='discrepancies')

@login_required
def auction_workspace(request):
 return render(request,'ui/auction_workspace.html',{
  'rules':AuctionRule.objects.order_by('-effective_year','-id'),
  'evaluations':AuctionEvaluation.objects.select_related('space','rule','evaluated_by').order_by('-evaluated_at')[:100],
  'periods':AuctionPeriod.objects.prefetch_related('lots__space').order_by('-id'),
 })

@login_required
@require_POST
def auction_evaluate(request):
 from django.core.exceptions import ValidationError
 from services.auctions import evaluate_space
 space=get_object_or_404(CommercialSpace,code=request.POST.get('space_code','').strip())
 try:evaluate_space(space=space,on_date=request.POST.get('on_date',''),auction_date=request.POST.get('auction_date',''),actor=request.user,ip_address=request.META.get('REMOTE_ADDR'))
 except (ValidationError,ValueError) as exc:messages.error(request,' '.join(getattr(exc,'messages',[str(exc)])))
 else:messages.success(request,'ارزیابی نسخه‌دار مزایده ثبت شد.')
 return redirect('auction-workspace')

@login_required
@require_POST
def auction_period_create(request):
 from django.core.exceptions import ValidationError
 from services.auctions import create_period
 try:create_period(identity=request.POST.get('identity',''),title=request.POST.get('title',''),planned_date=request.POST.get('planned_date',''),actor=request.user,ip_address=request.META.get('REMOTE_ADDR'))
 except ValidationError as exc:messages.error(request,' '.join(exc.messages))
 else:messages.success(request,'دوره مزایده ایجاد شد.')
 return redirect('auction-workspace')

@login_required
@require_POST
def auction_lot_add(request,period_id):
 from django.core.exceptions import ValidationError
 from services.auctions import add_evaluated_lot
 period=get_object_or_404(AuctionPeriod,pk=period_id)
 evaluation=get_object_or_404(AuctionEvaluation,pk=request.POST.get('evaluation_id'))
 try:add_evaluated_lot(period=period,evaluation=evaluation,actor=request.user,ip_address=request.META.get('REMOTE_ADDR'))
 except ValidationError as exc:messages.error(request,' '.join(exc.messages))
 else:messages.success(request,'فضای ارزیابی‌شده به دوره افزوده شد.')
 return redirect('auction-workspace')

@login_required
def commission_workspace(request):
 return render(request,'ui/commission_workspace.html',{
  'decisions':CommissionDecision.objects.prefetch_related('spaces').order_by('-id')[:100],
  'documents':Document.objects.filter(archived_at__isnull=True).order_by('-uploaded_at')[:100],
 })

@login_required
@require_POST
def commission_create(request):
 from django.core.exceptions import ValidationError
 from services.operations import create_commission_decision
 codes=[value.strip() for value in request.POST.get('space_codes','').replace('،',',').split(',') if value.strip()]
 spaces=list(CommercialSpace.objects.filter(code__in=codes))
 if len(spaces)!=len(set(codes)):
  messages.error(request,'یک یا چند کد فضا معتبر نیست.');return redirect('commission-workspace')
 document=Document.objects.filter(pk=request.POST.get('document_id'),archived_at__isnull=True).first() if request.POST.get('document_id') else None
 try:create_commission_decision(identity=request.POST.get('identity',''),decision_date=request.POST.get('decision_date',''),subject=request.POST.get('subject',''),decision_text=request.POST.get('decision',''),participants=request.POST.get('participants',''),subsequent_action=request.POST.get('subsequent_action',''),spaces=spaces,document=document,actor=request.user,ip_address=request.META.get('REMOTE_ADDR'))
 except ValidationError as exc:messages.error(request,' '.join(exc.messages))
 else:messages.success(request,'تصمیم کمیسیون با پیوند پرونده و ممیزی ثبت شد.')
 return redirect('commission-workspace')

@login_required
def report_builder(request):
 fields=[('code','کد فضا'),('name','نام فضا / مرکز'),('status','وضعیت'),('region','منطقه'),('current_usage','کاربری'),('area','مساحت')]
 return render(request,'ui/report_builder.html',{'fields':fields,'saved':SavedReport.objects.filter(owner=request.user)})
@login_required
@require_POST
def report_save(request):
 from services.reports import save_report
 name=request.POST.get('name','').strip()
 if not name: messages.error(request,'نام گزارش الزامی است.');return redirect('report-builder')
 save_report(owner=request.user,name=name,data=request.POST,ip_address=request.META.get('REMOTE_ADDR'))
 messages.success(request,'تعریف زنده گزارش ذخیره شد.');return redirect('report-builder')
@login_required
def report_open(request,report_id):
 from services.reports import report_query_string
 report=get_object_or_404(SavedReport,pk=report_id,owner=request.user)
 return redirect(f"/spaces/?{report_query_string(report)}")
@login_required
@require_POST
def report_archive(request,report_id):
 from services.reports import archive_report
 report=get_object_or_404(SavedReport,pk=report_id,owner=request.user)
 snapshot=archive_report(report=report,actor=request.user,ip_address=request.META.get('REMOTE_ADDR'))
 messages.success(request,f'نسخه ثابت با {snapshot.row_count} ردیف و اثر انگشت {snapshot.sha256[:12]} ثبت شد.')
 return redirect('report-builder')
def _query(request): return filter_spaces(request.GET)[:5000]
@login_required
def spaces_excel(request):return HttpResponse(excel(_query(request),request.GET.getlist('blank'),request.GET.getlist('field')),content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',headers={'Content-Disposition':'attachment; filename="spaces.xlsx"'})
@login_required
def spaces_docx(request):return HttpResponse(docx(_query(request),request.GET.getlist('blank'),request.GET.getlist('field')),content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document',headers={'Content-Disposition':'attachment; filename="spaces.docx"'})
@login_required
def spaces_pdf(request):return HttpResponse(pdf(_query(request),request.GET.getlist('field'),request.GET.getlist('blank')),content_type='application/pdf',headers={'Content-Disposition':'attachment; filename="spaces.pdf"'})
@login_required
@user_passes_test(lambda u:u.is_staff)
def user_list(request):
 from django.contrib.auth import get_user_model
 return render(request,'ui/user_list.html',{'users':get_user_model().objects.select_related('profile')})
@login_required
def password_change(request):
 form=PersianPasswordChangeForm(request.user,request.POST or None)
 if request.method=='POST' and form.is_valid():
  user=form.save();profile,_=UserProfile.objects.get_or_create(user=user,defaults={'display_name':user.get_full_name() or user.username});profile.must_change_password=False
  if not profile.display_name:profile.display_name=user.get_full_name() or user.username
  profile.save(update_fields=['must_change_password','display_name']);update_session_auth_hash(request,user);return redirect('dashboard')
 return render(request,'ui/password_change.html',{'form':form})

@login_required
@require_POST
def add_movement(request,code):
 from django.utils import timezone
 from django.db import transaction
 from services.dates import normalize_jalali
 from domains.identity.models import AuditEvent
 space=get_object_or_404(CommercialSpace,code=code)
 required=('location','holder','delivered_by','received_by','signature_state','direction')
 if any(not request.POST.get(field,'').strip() for field in required):
  messages.error(request,'تکمیل همه فیلدهای الزامی گردش پرونده لازم است.');return redirect('space-detail',code=code)
 due=request.POST.get('due_date','').strip()
 if due:
  try:due=normalize_jalali(due)
  except ValueError:messages.error(request,'تاریخ مهلت معتبر نیست.');return redirect('space-detail',code=code)
 with transaction.atomic():
  movement=FileMovement.objects.create(space=space,location=request.POST['location'].strip(),holder=request.POST['holder'].strip(),delivered_by=request.POST['delivered_by'].strip(),received_by=request.POST['received_by'].strip(),handover_at=timezone.now(),signature_state=request.POST['signature_state'].strip(),direction=request.POST['direction'].strip(),next_action=request.POST.get('next_action','').strip(),due_date=due,notes=request.POST.get('notes','').strip(),created_by=request.user)
  AuditEvent.objects.create(actor=request.user,action='FILE_MOVEMENT_CREATE',entity_type='CommercialSpace',entity_id=space.code,after={'movement_id':movement.pk,'holder':movement.holder,'location':movement.location},ip_address=request.META.get('REMOTE_ADDR'))
  from domains.operations.models import TimelineEvent
  TimelineEvent.objects.create(space=space,event_type='FILE_MOVEMENT_CREATE',jalali_date=due,occurred_at=movement.handover_at,source_entity='FileMovement',source_entity_id=str(movement.pk),title='ثبت گردش فیزیکی پرونده',description=f'{movement.holder} — {movement.location}',new_state=movement.direction,responsible_person=request.user.get_full_name() or request.user.username,provenance='رویداد عملیاتی ثبت‌شده در سامانه',target_url=f'/spaces/{space.code}/')
 messages.success(request,'گردش پرونده ثبت شد.');return redirect('space-detail',code=code)

@login_required
@require_POST
def upload_document(request,code):
 from django.core.exceptions import ValidationError
 from django.contrib import messages
 from services.documents import store_document
 space=get_object_or_404(CommercialSpace,code=code);uploaded=request.FILES.get('file')
 if not uploaded:messages.error(request,'فایل انتخاب نشده است.');return redirect('space-detail',code=code)
 try:store_document(uploaded=uploaded,title=request.POST.get('title','').strip() or uploaded.name,document_type=request.POST.get('document_type','سایر').strip(),entity_type='CommercialSpace',entity_id=space.code,user=request.user,ip_address=request.META.get('REMOTE_ADDR'))
 except ValidationError as exc:messages.error(request,' '.join(exc.messages))
 else:messages.success(request,'سند با ثبت checksum بارگذاری شد.')
 return redirect('space-detail',code=code)

@login_required
@require_POST
def add_contract(request,code):
 from django.core.exceptions import ValidationError
 from services.contracts import create_contract
 space=get_object_or_404(CommercialSpace,code=code)
 try:create_contract(space=space,actor=request.user,values=request.POST,ip_address=request.META.get('REMOTE_ADDR'))
 except ValidationError as exc:messages.error(request,' '.join(exc.messages))
 else:messages.success(request,'قرارداد عملیاتی و سابقه بهره‌بردار ثبت شد.')
 return redirect('space-detail',code=code)

@login_required
@require_POST
def add_contract_amendment(request,contract_id):
 from django.core.exceptions import ValidationError
 from services.contracts import add_amendment
 contract=get_object_or_404(Contract.objects.select_related('space'),pk=contract_id)
 try:add_amendment(contract=contract,actor=request.user,values=request.POST,ip_address=request.META.get('REMOTE_ADDR'))
 except ValidationError as exc:messages.error(request,' '.join(exc.messages))
 else:messages.success(request,'الحاقیه بدون تغییر سابقه قرارداد ثبت شد.')
 return redirect('space-detail',code=contract.space.code)

@login_required
@require_POST
def add_appraisal(request,code):
 from django.core.exceptions import ValidationError
 from services.operations import create_appraisal
 space=get_object_or_404(CommercialSpace,code=code);document=_owned_document(request.POST.get('document_id'),space)
 try:create_appraisal(space=space,actor=request.user,values=request.POST,document=document,ip_address=request.META.get('REMOTE_ADDR'))
 except ValidationError as exc:messages.error(request,' '.join(exc.messages))
 else:messages.success(request,'کارشناسی عملیاتی با خط زمانی ثبت شد.')
 return redirect('space-detail',code=code)

@login_required
@require_POST
def add_alert(request,code):
 from django.core.exceptions import ValidationError
 from services.operations import create_alert
 space=get_object_or_404(CommercialSpace,code=code)
 try:create_alert(space=space,actor=request.user,subject=request.POST.get('subject',''),reason=request.POST.get('reason',''),due_date=request.POST.get('due_date',''),ip_address=request.META.get('REMOTE_ADDR'))
 except ValidationError as exc:messages.error(request,' '.join(exc.messages))
 else:messages.success(request,'هشدار اقدام‌پذیر ثبت شد.')
 return redirect('space-detail',code=code)

@login_required
@require_POST
def change_space_status(request,code):
 from django.core.exceptions import ValidationError
 from services.properties import transition_space_status
 space=get_object_or_404(CommercialSpace,code=code);document=_owned_document(request.POST.get('document_id'),space)
 try:transition_space_status(space=space,actor=request.user,new_state=request.POST.get('new_state',''),effective_date=request.POST.get('effective_date',''),reason=request.POST.get('reason',''),document=document,ip_address=request.META.get('REMOTE_ADDR'))
 except ValidationError as exc:messages.error(request,' '.join(exc.messages))
 else:messages.success(request,'وضعیت canonical با حفظ سابقه تغییر کرد.')
 return redirect('space-detail',code=code)

@login_required
@require_POST
def add_utility(request,code):
 from django.core.exceptions import ValidationError
 from services.operations import record_utility
 space=get_object_or_404(CommercialSpace,code=code)
 document=_owned_document(request.POST.get('document_id'),space)
 try:record_utility(space=space,actor=request.user,values=request.POST,document=document,ip_address=request.META.get('REMOTE_ADDR'))
 except ValidationError as exc:messages.error(request,' '.join(exc.messages))
 else:messages.success(request,'رکورد مصرف و سهم‌ها ثبت شد.')
 return redirect('space-detail',code=code)

@login_required
@require_POST
def add_appraisal_fee(request,appraisal_id):
 from django.core.exceptions import ValidationError
 from services.operations import record_appraisal_fee
 appraisal=get_object_or_404(Appraisal.objects.select_related('space'),pk=appraisal_id)
 document=_owned_document(request.POST.get('document_id'),appraisal.space)
 try:record_appraisal_fee(appraisal=appraisal,actor=request.user,amount=request.POST.get('amount_rial',''),payment_status=request.POST.get('payment_status',''),payment_date=request.POST.get('payment_date',''),payment_reference=request.POST.get('payment_reference',''),follow_up_date=request.POST.get('follow_up_date',''),notes=request.POST.get('notes',''),document=document,ip_address=request.META.get('REMOTE_ADDR'))
 except ValidationError as exc:messages.error(request,' '.join(exc.messages))
 else:messages.success(request,'پرونده حق‌الزحمه کارشناسی ثبت شد.')
 return redirect('space-detail',code=appraisal.space.code)

def _owned_document(document_id,space):
 if not document_id:return None
 return get_object_or_404(Document,pk=document_id,entity_type='CommercialSpace',entity_id=space.code,archived_at__isnull=True)

@login_required
@require_POST
def workflow_create(request,code):
 from django.core.exceptions import ValidationError
 from services.operations import create_workflow
 space=get_object_or_404(CommercialSpace,code=code)
 try:create_workflow(space=space,actor=request.user,process_type=request.POST.get('process_type',''),title=request.POST.get('title',''),next_action=request.POST.get('next_action',''),due_date=request.POST.get('due_date',''),ip_address=request.META.get('REMOTE_ADDR'))
 except ValidationError as exc:messages.error(request,' '.join(exc.messages))
 else:messages.success(request,'فرایند عملیاتی ایجاد شد.')
 return redirect('space-detail',code=code)

@login_required
@require_POST
def commission_transition(request,decision_id):
 from django.core.exceptions import ValidationError
 from services.operations import transition_commission
 decision=get_object_or_404(CommissionDecision,pk=decision_id)
 try:transition_commission(decision=decision,actor=request.user,new_state=request.POST.get('state',''),subsequent_action=request.POST.get('subsequent_action',''),reason=request.POST.get('reason',''),ip_address=request.META.get('REMOTE_ADDR'))
 except ValidationError as exc:messages.error(request,' '.join(exc.messages))
 else:messages.success(request,'وضعیت تصمیم کمیسیون ثبت شد.')
 space=decision.spaces.first();return redirect('space-detail',code=space.code) if space else redirect('domain-list',domain='commissions')

@login_required
@require_POST
def alert_resolve(request,alert_id):
 from django.core.exceptions import ValidationError
 from services.operations import resolve_alert
 alert=get_object_or_404(Alert.objects.select_related('space'),pk=alert_id)
 try:resolve_alert(alert=alert,actor=request.user,reason=request.POST.get('reason',''),ip_address=request.META.get('REMOTE_ADDR'))
 except ValidationError as exc:messages.error(request,' '.join(exc.messages))
 else:messages.success(request,'هشدار پس از ثبت اقدام مختومه شد.')
 return redirect('space-detail',code=alert.space.code)

@login_required
@require_POST
def workflow_transition(request,workflow_id):
 from django.core.exceptions import ValidationError
 from services.operations import transition_workflow
 workflow=get_object_or_404(WorkflowInstance.objects.select_related('space'),pk=workflow_id)
 try:transition_workflow(workflow=workflow,actor=request.user,new_state=request.POST.get('state',''),next_action=request.POST.get('next_action',''),due_date=request.POST.get('due_date',''),ip_address=request.META.get('REMOTE_ADDR'))
 except ValidationError as exc:messages.error(request,' '.join(exc.messages))
 else:messages.success(request,'وضعیت فرایند با ثبت رویداد ممیزی تغییر کرد.')
 return redirect('space-detail',code=workflow.space.code)

@login_required
@user_passes_test(lambda u:u.is_staff)
@require_POST
def user_create(request):
 from django.contrib.auth import get_user_model
 from django.db import transaction
 from domains.identity.models import AuditEvent
 import secrets
 username=request.POST.get('username','').strip(); display=request.POST.get('display_name','').strip()
 if not username or not display:
  messages.error(request,'نام کاربری و نام نمایشی الزامی است.');return redirect('user-list')
 if get_user_model().objects.filter(username=username).exists():
  messages.error(request,'این نام کاربری قبلاً ثبت شده است.');return redirect('user-list')
 temporary=secrets.token_urlsafe(18)
 with transaction.atomic():
  user=get_user_model().objects.create_user(username=username,password=temporary,first_name=display)
  UserProfile.objects.create(user=user,display_name=display,must_change_password=True,operational_access=True)
  AuditEvent.objects.create(actor=request.user,action='USER_CREATE',entity_type='User',entity_id=str(user.pk),reason='ایجاد کاربر از مدیریت بومی سما',after={'username':username,'active':True},ip_address=request.META.get('REMOTE_ADDR'))
 messages.success(request,f'کاربر ایجاد شد. گذرواژه موقت فقط همین بار نمایش داده می‌شود: {temporary}')
 return redirect('user-list')

@login_required
@user_passes_test(lambda u:u.is_staff)
@require_POST
def user_reset_password(request,user_id):
 from django.contrib.auth import get_user_model
 from domains.identity.models import AuditEvent
 import secrets
 target=get_object_or_404(get_user_model(),pk=user_id); temporary=secrets.token_urlsafe(18);target.set_password(temporary);target.save(update_fields=['password']); profile,_=UserProfile.objects.get_or_create(user=target,defaults={'display_name':target.get_full_name() or target.username});profile.must_change_password=True;profile.save(update_fields=['must_change_password'])
 AuditEvent.objects.create(actor=request.user,action='USER_PASSWORD_RESET',entity_type='User',entity_id=str(target.pk),reason=request.POST.get('reason','بازنشانی مدیریتی').strip(),after={'must_change_password':True},ip_address=request.META.get('REMOTE_ADDR'))
 messages.success(request,f'گذرواژه موقت {target.username} فقط همین بار: {temporary}');return redirect('user-list')

@login_required
@user_passes_test(lambda u:u.is_staff)
@require_POST
def user_toggle_active(request,user_id):
 from django.contrib.auth import get_user_model
 from domains.identity.models import AuditEvent
 target=get_object_or_404(get_user_model(),pk=user_id)
 if target==request.user:
  messages.error(request,'مدیر نمی‌تواند حساب جاری خود را غیرفعال کند.');return redirect('user-list')
 before=target.is_active;target.is_active=not before;target.save(update_fields=['is_active']);AuditEvent.objects.create(actor=request.user,action='USER_STATUS_CHANGE',entity_type='User',entity_id=str(target.pk),reason=request.POST.get('reason','تغییر وضعیت دسترسی').strip(),before={'active':before},after={'active':target.is_active},ip_address=request.META.get('REMOTE_ADDR'));messages.success(request,'وضعیت کاربر تغییر کرد.');return redirect('user-list')
