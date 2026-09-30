from django.contrib.auth.decorators import login_required,user_passes_test
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import render,get_object_or_404,redirect
from django.db.models import Count
from domains.properties.models import CommercialSpace,Region,Center,MotherProperty
from domains.registry.models import Discrepancy
from domains.identity.models import UserProfile, SavedReport, ArchivedReportSnapshot
from domains.contracts.models import Contract, Beneficiary
from domains.operations.models import Appraisal, AppraisalFee, Auction, CommissionDecision, UtilityRecord, UtilityObligation, FileMovement, WorkflowInstance, Alert, DecisionOrder
from domains.documents.models import Document
from queries.spaces import filter_spaces
from services.file_movement import current_holder
from reporting.engine import excel,docx,pdf
@login_required
def dashboard(request):
 context={'space_count':CommercialSpace.objects.count(),'active_count':CommercialSpace.objects.filter(status='ACTIVE').count(),'inactive_count':CommercialSpace.objects.filter(status='OUT_OF_CYCLE').count(),'property_count':MotherProperty.objects.count(),'discrepancy_count':Discrepancy.objects.exclude(status='RESOLVED').count()}
 return render(request,'ui/dashboard.html',context)
@login_required
def space_list(request):
 qs=filter_spaces(request.GET);page=Paginator(qs,25).get_page(request.GET.get('page'))
 return render(request,'ui/space_list.html',{'page':page,'regions':Region.objects.all(),'centers':Center.objects.filter(is_special=True),'total':qs.count()})
@login_required
def space_detail(request,code):
 s=get_object_or_404(CommercialSpace.objects.select_related('region','center').prefetch_related('status_history','contracts__amendments','beneficiary_assignments__beneficiary','appraisals','auctions','utilities','utility_obligations','decisions','commission_decisions','timeline','alerts','file_movements','workflows','source_documents','property_links__mother_property'),code=code)
 return render(request,'ui/space_detail.html',{'space':s,'holder':current_holder(s),'uploaded_documents':Document.objects.filter(entity_type='CommercialSpace',entity_id=s.code,archived_at__isnull=True)})

DOMAIN_LISTS={
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
 for part in path.split('.'):
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
def report_builder(request):
 fields=[('code','کد فضا'),('name','نام فضا / مرکز'),('status','وضعیت'),('region','منطقه'),('current_usage','کاربری'),('area','مساحت')]
 return render(request,'ui/report_builder.html',{'fields':fields,'saved':SavedReport.objects.filter(owner=request.user)})
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
 form=PasswordChangeForm(request.user,request.POST or None)
 if request.method=='POST' and form.is_valid():
  user=form.save(); UserProfile.objects.update_or_create(user=user,defaults={'must_change_password':False,'display_name':user.get_full_name() or user.username});update_session_auth_hash(request,user);return redirect('dashboard')
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
def add_utility(request,code):
 from django.core.exceptions import ValidationError
 from services.operations import record_utility
 space=get_object_or_404(CommercialSpace,code=code)
 try:record_utility(space=space,actor=request.user,values=request.POST,ip_address=request.META.get('REMOTE_ADDR'))
 except ValidationError as exc:messages.error(request,' '.join(exc.messages))
 else:messages.success(request,'رکورد مصرف و سهم‌ها ثبت شد.')
 return redirect('space-detail',code=code)

@login_required
@require_POST
def add_appraisal_fee(request,appraisal_id):
 from django.core.exceptions import ValidationError
 from services.operations import record_appraisal_fee
 appraisal=get_object_or_404(Appraisal.objects.select_related('space'),pk=appraisal_id)
 try:record_appraisal_fee(appraisal=appraisal,actor=request.user,amount=request.POST.get('amount_rial',''),payment_status=request.POST.get('payment_status',''),payment_date=request.POST.get('payment_date',''),payment_reference=request.POST.get('payment_reference',''),follow_up_date=request.POST.get('follow_up_date',''),notes=request.POST.get('notes',''),ip_address=request.META.get('REMOTE_ADDR'))
 except ValidationError as exc:messages.error(request,' '.join(exc.messages))
 else:messages.success(request,'پرونده حق‌الزحمه کارشناسی ثبت شد.')
 return redirect('space-detail',code=appraisal.space.code)

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
