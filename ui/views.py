from django.contrib.auth.decorators import login_required,user_passes_test
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.core.paginator import Paginator
from django.http import HttpResponse, FileResponse
from django.shortcuts import render,get_object_or_404,redirect
from django.urls import reverse
from django.db.models import Count,Q,IntegerField
from django.db.models.functions import Cast
from domains.properties.models import CommercialSpace,Region,Center,MotherProperty
from domains.registry.models import Discrepancy
from domains.identity.models import UserProfile, SavedFilter, SavedReport, ArchivedReportSnapshot
from domains.contracts.models import Contract, Beneficiary
from domains.operations.models import Appraisal, AppraisalFee, Auction, AuctionEvaluation, AuctionPeriod, AuctionRule, CommissionDecision, UtilityRecord, UtilityObligation, FileMovement, WorkflowInstance, Alert, DecisionOrder
from domains.documents.models import Document
from queries.spaces import filter_spaces
from services.file_movement import current_holder
from reporting.engine import excel,docx,pdf,tabular_excel,output_table,MOTHER_FIELD_MAP
from ui.forms import PersianPasswordChangeForm
from core.uat import is_fixed_uat_admin
from services.money import format_rial
@login_required
def dashboard(request):
 spaces=CommercialSpace.objects.all();active=spaces.filter(status='ACTIVE')
 region_rows=list(active.exclude(region=None).values('region__name').annotate(total=Count('id')).order_by('-total')[:5]);maximum=max((row['total'] for row in region_rows),default=1)
 for row in region_rows:row['percent']=round(row['total']*100/maximum)
 context={'space_count':spaces.count(),'active_count':active.count(),'inactive_count':spaces.filter(status='OUT_OF_CYCLE').count(),'property_count':MotherProperty.objects.count(),'discrepancy_count':Discrepancy.objects.exclude(status='RESOLVED').count(),'contract_count':Contract.objects.count(),'appraisal_count':Appraisal.objects.count(),'alert_count':Alert.objects.exclude(status='RESOLVED').count(),'without_contract_count':active.filter(contracts__isnull=True).count(),'without_appraisal_count':active.filter(appraisals__isnull=True).count(),'open_workflow_count':WorkflowInstance.objects.filter(state='OPEN').count(),'region_rows':region_rows}
 return render(request,'ui/dashboard.html',context)
@login_required
def regions_workspace(request):
 regions=Region.objects.annotate(region_numeric=Cast("code",IntegerField()),space_count=Count("commercialspace",distinct=True),property_count=Count("motherproperty",distinct=True)).order_by("region_numeric","name")
 return render(request,"ui/regions_workspace.html",{"regions":regions,"special_count":Center.objects.filter(is_special=True).count()})

def _management_context(spaces):
 active=spaces.filter(status="ACTIVE")
 return {"space_count":spaces.count(),"active_count":active.count(),"inactive_count":spaces.filter(status="OUT_OF_CYCLE").count(),"property_count":MotherProperty.objects.filter(space_links__space__in=spaces).distinct().count(),"contract_count":Contract.objects.filter(space__in=spaces).count(),"appraisal_count":Appraisal.objects.filter(space__in=spaces).count(),"without_contract_count":active.filter(contracts__isnull=True).count(),"without_appraisal_count":active.filter(appraisals__isnull=True).count(),"workflow_count":WorkflowInstance.objects.filter(space__in=spaces,state="OPEN").count(),"alert_count":Alert.objects.filter(space__in=spaces).exclude(status="RESOLVED").count(),"document_count":Document.objects.filter(entity_type="CommercialSpace",entity_id__in=spaces.values("code")).count()}

@login_required
def region_workspace(request,region_id):
 region=get_object_or_404(Region,pk=region_id);spaces=CommercialSpace.objects.filter(region=region,center__is_special=False)
 return render(request,"ui/management_workspace.html",{"scope_title":f"{region.name} — نمای مدیریتی","scope_kind":"region","scope_id":region.pk,"spaces":spaces[:25],**_management_context(spaces)})

@login_required
def special_centers_workspace(request):
 centers=Center.objects.filter(is_special=True).select_related("region").annotate(region_numeric=Cast("region__code",IntegerField()),space_count=Count("commercialspace")).order_by("region_numeric","name")
 return render(request,"ui/special_centers_workspace.html",{"centers":centers})

@login_required
def special_center_workspace(request,center_id):
 center=get_object_or_404(Center.objects.select_related("region"),pk=center_id,is_special=True);spaces=CommercialSpace.objects.filter(center=center)
 return render(request,"ui/management_workspace.html",{"scope_title":f"{center.name} — نمای مدیریتی مرکز خاص","scope_kind":"center","scope_id":center.pk,"center":center,"spaces":spaces[:25],**_management_context(spaces)})

@login_required
def mother_property_list(request):
 from queries.mother_properties import filter_mother_properties
 qs=filter_mother_properties(request.GET);page=Paginator(qs,25).get_page(request.GET.get('page'))
 available=(('name','نام'),('region','منطقه'),('usage','کاربری'),('area','مساحت'),('space_count','فضاهای مرتبط'))
 requested=[value for value in request.GET.getlist('column') if value in dict(available)]
 return render(request,'ui/mother_property_list.html',{'page':page,'total':qs.count(),'dataset_total':MotherProperty.objects.count(),'regions':Region.objects.order_by('name'),'available_columns':available,'visible_columns':requested or [x[0] for x in available]})

@login_required
def mother_property_detail(request,identifier):
 item=get_object_or_404(MotherProperty.objects.select_related('region').prefetch_related('space_links__space__beneficiary_assignments__beneficiary'),identifier=identifier)
 documents=Document.objects.filter(entity_type='MotherProperty',entity_id=item.identifier,archived_at__isnull=True)
 return render(request,'ui/mother_property_detail.html',{'property':item,'documents':documents})

def _mother_query(request):
 from queries.mother_properties import filter_mother_properties
 return filter_mother_properties(request.GET)[:5000]
@login_required
def mother_report(request):
 fields=[(key,label) for key,(label,_) in MOTHER_FIELD_MAP.items()]
 return render(request,'ui/mother_property_report.html',{'fields':fields,'query':request.GET.urlencode()})
@login_required
def mother_report_preview(request):
 labels,rows=output_table(_mother_query(request)[:100],request.GET.getlist('layout'),request.GET.getlist('field'),request.GET.getlist('blank'),MOTHER_FIELD_MAP,request.GET.get('blank_rows',0))
 return render(request,'ui/report_preview.html',{'labels':labels,'rows':rows,'query':request.GET.urlencode(),'export_prefix':'mother-properties'})
@login_required
def mother_excel(request):return HttpResponse(excel(_mother_query(request),request.GET.getlist('blank'),request.GET.getlist('field'),request.GET.getlist('layout'),request.GET.get('orientation','landscape'),MOTHER_FIELD_MAP,'املاک مادر',request.GET.get('blank_rows',0)),content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',headers={'Content-Disposition':'attachment; filename="mother-properties.xlsx"'})
@login_required
def mother_docx(request):return HttpResponse(docx(_mother_query(request),request.GET.getlist('blank'),request.GET.getlist('field'),request.GET.getlist('layout'),request.GET.get('orientation','landscape'),MOTHER_FIELD_MAP,request.GET.get('blank_rows',0)),content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document',headers={'Content-Disposition':'attachment; filename="mother-properties.docx"'})
@login_required
def mother_pdf(request):return HttpResponse(pdf(_mother_query(request),request.GET.getlist('field'),request.GET.getlist('blank'),request.GET.getlist('layout'),request.GET.get('orientation','landscape'),MOTHER_FIELD_MAP,request.GET.get('blank_rows',0)),content_type='application/pdf',headers={'Content-Disposition':'attachment; filename="mother-properties.pdf"'})
@login_required
def space_list(request):
 qs=filter_spaces(request.GET);page=Paginator(qs,25).get_page(request.GET.get('page'))
 allowed_columns={'name','status','region','usage','area'}
 requested=set(request.GET.getlist('column')) & allowed_columns
 visible=requested or allowed_columns
 return render(request,'ui/space_list.html',{'page':page,'regions':Region.objects.all(),'centers':Center.objects.filter(is_special=True),'total':qs.count(),'dataset_total':CommercialSpace.objects.count(),'saved_filters':SavedFilter.objects.filter(owner=request.user,domain='spaces'),'visible_columns':visible})

OPERATION_CONFIG={
 'contract':{'title':'ثبت قرارداد جدید','submit_label':'ثبت قرارداد','domain':'contracts','module_title':'قراردادها','section':'contracts','requires_space':True,'post_name':'add-contract'},
 'beneficiary':{'title':'ثبت و پیوند بهره‌بردار','submit_label':'ثبت بهره‌بردار','domain':'beneficiaries','module_title':'بهره‌برداران','section':'contracts','requires_space':True,'post_name':'add-beneficiary'},
 'appraisal':{'title':'ثبت کارشناسی جدید','submit_label':'ثبت کارشناسی','domain':'appraisals','module_title':'کارشناسی','section':'appraisals','requires_space':True,'post_name':'add-appraisal'},
 'appraisal_fee':{'title':'ثبت حق‌الزحمه کارشناسی','submit_label':'ثبت حق‌الزحمه','domain':'fees','module_title':'حق‌الزحمه کارشناسی','section':'appraisals','requires_space':False,'post_name':'add-appraisal-fee'},
 'amendment':{'title':'ثبت الحاقیه قرارداد','submit_label':'ثبت الحاقیه','domain':'contracts','module_title':'قراردادها','section':'contracts','requires_space':False,'post_name':'add-contract-amendment'},
 'document':{'title':'بارگذاری سند','submit_label':'بارگذاری امن سند','domain':'documents','module_title':'مدارک و مستندات','section':'documents','requires_space':True,'post_name':'upload-document'},
 'utility':{'title':'ثبت انشعاب یا مصرف','submit_label':'ثبت اطلاعات مصرف','domain':'utilities','module_title':'انشعابات و مصرف','section':'utilities','requires_space':True,'post_name':'add-utility'},
 'movement':{'title':'ثبت تحویل پرونده','submit_label':'ثبت تحویل','domain':'workflows','module_title':'پیگیری پرونده','section':'workflows','requires_space':True,'post_name':'add-movement'},
 'workflow':{'title':'ثبت فرایند پیگیری','submit_label':'ثبت فرایند','domain':'workflows','module_title':'پیگیری پرونده','section':'workflows','requires_space':True,'post_name':'workflow-create'},
 'alert':{'title':'ثبت مورد نیازمند پیگیری','submit_label':'ثبت مورد پیگیری','domain':'alerts','module_title':'موارد نیازمند پیگیری','section':'alerts','requires_space':True,'post_name':'add-alert'},
}

@login_required
def operation_create(request,action):
 operation=OPERATION_CONFIG.get(action)
 if not operation:return HttpResponse(status=404)
 space=None;contract=None;appraisal=None;beneficiary=None
 if request.GET.get('space'):space=get_object_or_404(CommercialSpace,code=request.GET['space'])
 kwargs={}
 if action=='beneficiary' and request.GET.get('beneficiary'):
  beneficiary=get_object_or_404(Beneficiary,pk=request.GET['beneficiary']);assignment=beneficiary.beneficiaryassignment_set.select_related('space').order_by('-pk').first();space=assignment.space if assignment else space
  operation={**operation,'title':'ویرایش مشخصات بهره‌بردار','submit_label':'ثبت ویرایش'};kwargs={'beneficiary_id':beneficiary.pk};operation['post_name']='update-beneficiary'
 if action=='amendment':
  contract=get_object_or_404(Contract.objects.select_related('space'),pk=request.GET.get('contract'));space=contract.space;kwargs={'contract_id':contract.pk}
 elif action=='appraisal_fee':
  appraisal=get_object_or_404(Appraisal.objects.select_related('space'),pk=request.GET.get('appraisal'));space=appraisal.space;kwargs={'appraisal_id':appraisal.pk}
 elif space:kwargs={'code':space.code}
 operation={**operation,'post_url':reverse(operation['post_name'],kwargs=kwargs) if kwargs else ''}
 return render(request,'ui/operation_form.html',{'action':action,'operation':operation,'space':space,'contract':contract,'appraisal':appraisal,'beneficiary':beneficiary,'spaces':filter_spaces({})})

@login_required
def space_detail(request,code):
 s=get_object_or_404(CommercialSpace.objects.select_related('region','center').prefetch_related('status_history','contracts__amendments','contracts__beneficiary','contract_circulations__transfers','contract_circulations__signature_steps','beneficiary_assignments__beneficiary','appraisals__fee__supporting_document','auctions','utilities__supporting_document','utility_obligations','decisions','commission_decisions__spaces','timeline__document','alerts__assigned_to','file_movements','workflows','source_documents','property_links__mother_property'),code=code)
 timeline=s.timeline.all();event_type=request.GET.get('event_type','').strip()
 undated=timeline.filter(jalali_date='')
 dated=timeline.exclude(jalali_date='')
 if event_type=='UNDATED':dated=timeline.none()
 elif event_type:dated=dated.filter(event_type=event_type)
 event_types=s.timeline.exclude(jalali_date='').order_by().values_list('event_type',flat=True).distinct()
 return render(request,'ui/space_detail.html',{'space':s,'holder':current_holder(s),'timeline_events':dated,'undated_events':undated,'event_types':event_types,'uploaded_documents':Document.objects.filter(entity_type='CommercialSpace',entity_id=s.code,archived_at__isnull=True),'history':__import__('domains.operations.models',fromlist=['OperationalHistory']).OperationalHistory.objects.filter(entity_type__in=['WorkflowInstance','AppraisalFee','UtilityRecord','CommissionDecision','Alert'])[:100]})

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
 'alerts':('موارد نیازمند پیگیری',Alert.objects.select_related('space','assigned_to'),(('space.code','کد فضا'),('subject','موضوع'),('reason','علت'),('due_date','سررسید'),('priority','اولویت'),('status','وضعیت'),('assigned_to.username','مسئول پیگیری'))),
 'documents':('اسناد بارگذاری‌شده',Document.objects.all(),(('title','عنوان'),('document_type','نوع'),('original_filename','نام فایل'),('uploaded_at','زمان بارگذاری'))),
}
def _value(obj,path):
 parts=path.split('.')
 for index,part in enumerate(parts):
  display=getattr(obj,f'get_{part}_display',None) if index==len(parts)-1 else None
  if display:return display()
  obj=getattr(obj,part,None)
  if obj is None:return '—'
 if obj in ('',None):return '—'
 if path.endswith(('amount_rial','investment_commitment_rial','bill_amount_rial')):return format_rial(obj)
 return obj
def _search_domain(qs,domain,q):
 if not q:return qs
 if domain=='contracts':return qs.filter(Q(number__icontains=q)|Q(space__code__iexact=q))
 if domain in {'appraisals','fees','auctions','utilities','workflows','alerts'}:
  field='appraisal__space__code__iexact' if domain=='fees' else 'space__code__iexact'
  return qs.filter(**{field:q})
 if domain=='beneficiaries':return qs.filter(Q(name__icontains=q)|Q(beneficiaryassignment__space__code__iexact=q)).distinct()
 if domain=='documents':return qs.filter(Q(title__icontains=q)|Q(entity_type='CommercialSpace',entity_id__iexact=q))
 return qs
@login_required
def domain_list(request,domain):
 title,qs,columns=DOMAIN_LISTS[domain]
 dataset_count=qs.count()
 q=request.GET.get('q','').strip()
 qs=_search_domain(qs,domain,q)
 region_id=request.GET.get('region_id');center_id=request.GET.get('center_id')
 if domain in {'contracts','appraisals','auctions','utilities','workflows','alerts'}:
  if region_id:qs=qs.filter(space__region_id=region_id)
  if center_id:qs=qs.filter(space__center_id=center_id)
 elif domain=='fees':
  if region_id:qs=qs.filter(appraisal__space__region_id=region_id)
  if center_id:qs=qs.filter(appraisal__space__center_id=center_id)
 elif domain=='beneficiaries':
  if region_id:qs=qs.filter(beneficiaryassignment__space__region_id=region_id).distinct()
  if center_id:qs=qs.filter(beneficiaryassignment__space__center_id=center_id).distinct()
 elif domain=='documents':
  space_codes=CommercialSpace.objects.all()
  if region_id:space_codes=space_codes.filter(region_id=region_id)
  if center_id:space_codes=space_codes.filter(center_id=center_id)
  if region_id or center_id:qs=qs.filter(entity_type='CommercialSpace',entity_id__in=space_codes.values('code'))
 if domain=='alerts' and request.GET.get('state')=='OPEN':qs=qs.exclude(status='RESOLVED')
 if domain=='workflows' and request.GET.get('state')=='OPEN':qs=qs.filter(state='OPEN')
 if domain=='contracts':
  if request.GET.get('space_code'):qs=qs.filter(space__code__iexact=request.GET['space_code'])
  if request.GET.get('number'):qs=qs.filter(number__icontains=request.GET['number'])
  if request.GET.get('beneficiary'):qs=qs.filter(beneficiary__name__icontains=request.GET['beneficiary'])
  if request.GET.get('status'):qs=qs.filter(status__icontains=request.GET['status'])
  if request.GET.get('origin')=='historical':qs=qs.filter(is_historical=True)
  elif request.GET.get('origin')=='operational':qs=qs.filter(is_historical=False)
  if request.GET.get('number_presence')=='missing':qs=qs.filter(number='')
  elif request.GET.get('number_presence')=='present':qs=qs.exclude(number='')
 if domain=='beneficiaries':
  if request.GET.get('identifier'):qs=qs.filter(identity_number__icontains=request.GET['identifier'])
  if request.GET.get('kind'):qs=qs.filter(kind=request.GET['kind'])
  if request.GET.get('space_code'):qs=qs.filter(beneficiaryassignment__space__code__iexact=request.GET['space_code']).distinct()
 if domain=='appraisals':
  if request.GET.get('space_code'):qs=qs.filter(space__code__iexact=request.GET['space_code'])
  if request.GET.get('appraiser'):qs=qs.filter(appraiser__icontains=request.GET['appraiser'])
  if request.GET.get('status'):qs=qs.filter(status__icontains=request.GET['status'])
  if request.GET.get('missing')=='date':qs=qs.filter(appraisal_date='')
  elif request.GET.get('missing')=='appraiser':qs=qs.filter(appraiser='')
  elif request.GET.get('missing')=='zero':qs=qs.filter(amount_rial=0)
 page=Paginator(qs.order_by('-pk'),30).get_page(request.GET.get('page'))
 rows=[]
 for obj in page:
  space=getattr(obj,'space',None)
  if domain=='fees':space=obj.appraisal.space
  elif domain=='documents' and obj.entity_type=='CommercialSpace':space=CommercialSpace.objects.filter(code=obj.entity_id).first()
  elif domain=='beneficiaries':space=CommercialSpace.objects.filter(beneficiary_assignments__beneficiary=obj).order_by('code').first()
  rows.append({'object':obj,'values':[_value(obj,key) for key,_ in columns],'space_code':space.code if space else ''})
 actions={'contracts':('contract','ثبت قرارداد'),'beneficiaries':('beneficiary','ثبت بهره‌بردار'),'appraisals':('appraisal','ثبت کارشناسی'),'utilities':('utility','ثبت انشعاب / مصرف'),'workflows':('movement','ثبت تحویل پرونده'),'documents':('document','بارگذاری سند'),'alerts':('alert','ثبت مورد پیگیری')}
 return render(request,'ui/domain_list.html',{'title':title,'headers':[label for _,label in columns],'rows':rows,'page':page,'domain':domain,'dataset_count':dataset_count,'has_filter':bool(q) or bool(request.GET.get('state')),'create_action':actions.get(domain)})

@login_required
def domain_excel(request,domain):
 if domain not in DOMAIN_LISTS:return HttpResponse(status=404)
 title,qs,columns=DOMAIN_LISTS[domain]
 q=request.GET.get('q','').strip()
 qs=_search_domain(qs,domain,q)
 region_id=request.GET.get('region_id');center_id=request.GET.get('center_id')
 if domain in {'contracts','appraisals','auctions','utilities','workflows','alerts'}:
  if region_id:qs=qs.filter(space__region_id=region_id)
  if center_id:qs=qs.filter(space__center_id=center_id)
 elif domain=='fees':
  if region_id:qs=qs.filter(appraisal__space__region_id=region_id)
  if center_id:qs=qs.filter(appraisal__space__center_id=center_id)
 elif domain=='beneficiaries':
  if region_id:qs=qs.filter(beneficiaryassignment__space__region_id=region_id).distinct()
  if center_id:qs=qs.filter(beneficiaryassignment__space__center_id=center_id).distinct()
 elif domain=='documents':
  space_codes=CommercialSpace.objects.all()
  if region_id:space_codes=space_codes.filter(region_id=region_id)
  if center_id:space_codes=space_codes.filter(center_id=center_id)
  if region_id or center_id:qs=qs.filter(entity_type='CommercialSpace',entity_id__in=space_codes.values('code'))
 labels=[label for _,label in columns]
 data=([_value(item,key) for key,_ in columns] for item in qs.order_by('pk')[:10000])
 return HttpResponse(tabular_excel(title,labels,data),content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',headers={'Content-Disposition':f'attachment; filename="{domain}.xlsx"'})

@login_required
def document_download(request,document_id):
 document=get_object_or_404(Document,pk=document_id,archived_at__isnull=True)
 return FileResponse(document.file.open('rb'),content_type=document.content_type,as_attachment=True,filename=document.original_filename)

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
  'spaces':filter_spaces({}),
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
  'spaces':filter_spaces({}),
 })

@login_required
@require_POST
def commission_create(request):
 from django.core.exceptions import ValidationError
 from services.operations import create_commission_decision
 codes=[part.strip() for value in request.POST.getlist('space_codes') for part in value.replace('،',',').split(',') if part.strip()]
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
 return render(request,'ui/report_builder.html',{'fields':fields,'saved':SavedReport.objects.filter(owner=request.user),'report_domains':[(key,DOMAIN_LISTS[key][0]) for key in ('contracts','beneficiaries','appraisals','fees','auctions','utilities','workflows','documents','alerts')]})
@login_required
def report_preview(request):
 labels,rows=output_table(_query(request)[:100],request.GET.getlist('layout'),request.GET.getlist('field'),request.GET.getlist('blank'),blank_rows=request.GET.get('blank_rows',0))
 return render(request,'ui/report_preview.html',{'labels':labels,'rows':rows,'query':request.GET.urlencode()})
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
 return redirect(f"/{'mother-properties/report/preview' if report.domain=='mother_properties' else 'spaces/'}?{report_query_string(report)}")
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
def spaces_excel(request):return HttpResponse(excel(_query(request),request.GET.getlist('blank'),request.GET.getlist('field'),request.GET.getlist('layout'),request.GET.get('orientation','landscape'),blank_rows=request.GET.get('blank_rows',0)),content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',headers={'Content-Disposition':'attachment; filename="spaces.xlsx"'})
@login_required
def spaces_docx(request):return HttpResponse(docx(_query(request),request.GET.getlist('blank'),request.GET.getlist('field'),request.GET.getlist('layout'),request.GET.get('orientation','landscape'),blank_rows=request.GET.get('blank_rows',0)),content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document',headers={'Content-Disposition':'attachment; filename="spaces.docx"'})
@login_required
def spaces_pdf(request):return HttpResponse(pdf(_query(request),request.GET.getlist('field'),request.GET.getlist('blank'),request.GET.getlist('layout'),request.GET.get('orientation','landscape'),blank_rows=request.GET.get('blank_rows',0)),content_type='application/pdf',headers={'Content-Disposition':'attachment; filename="spaces.pdf"'})
@login_required
@user_passes_test(lambda u:u.is_staff)
def user_list(request):
 from django.contrib.auth import get_user_model
 return render(request,'ui/user_list.html',{'users':get_user_model().objects.select_related('profile')})
@login_required
def account_detail(request):
 return render(request,'ui/account_detail.html')

@login_required
def password_change(request):
 if is_fixed_uat_admin(request.user):
  messages.info(request,'گذرواژه مدیر ثابت نسخه UAT از رابط کاربری قابل تغییر نیست.');return redirect('dashboard')
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
def update_beneficiary(request,beneficiary_id):
 from domains.identity.models import AuditEvent
 beneficiary=get_object_or_404(Beneficiary,pk=beneficiary_id);name=request.POST.get('name','').strip();kind=request.POST.get('kind','')
 if not name or kind not in Beneficiary.Kind.values:
  messages.error(request,'نام و نوع بهره‌بردار معتبر الزامی است.');return redirect(f"{reverse('operation-create',kwargs={'action':'beneficiary'})}?beneficiary={beneficiary.pk}")
 before={'name':beneficiary.name,'kind':beneficiary.kind,'identity_number':beneficiary.identity_number,'contact':beneficiary.contact}
 beneficiary.name=name;beneficiary.kind=kind;beneficiary.identity_number=request.POST.get('identity_number','').strip();beneficiary.contact=request.POST.get('contact','').strip();beneficiary.save(update_fields=['name','kind','identity_number','contact'])
 AuditEvent.objects.create(actor=request.user,action='BENEFICIARY_UPDATE',entity_type='Beneficiary',entity_id=str(beneficiary.pk),before=before,after={'name':name,'kind':kind},ip_address=request.META.get('REMOTE_ADDR'))
 assignment=beneficiary.beneficiaryassignment_set.select_related('space').order_by('-pk').first();messages.success(request,'مشخصات بهره‌بردار ویرایش شد.')
 return redirect('space-detail',code=assignment.space.code) if assignment else redirect('domain-list',domain='beneficiaries')

@login_required
@require_POST
def add_beneficiary(request,code):
 from django.core.exceptions import ValidationError
 from django.db import transaction
 from services.dates import normalize_jalali
 from domains.contracts.models import BeneficiaryAssignment
 from domains.identity.models import AuditEvent
 from domains.operations.models import TimelineEvent
 space=get_object_or_404(CommercialSpace,code=code);name=request.POST.get('name','').strip();kind=request.POST.get('kind','')
 if not name or kind not in Beneficiary.Kind.values:
  messages.error(request,'نام و نوع بهره‌بردار معتبر الزامی است.');return redirect('operation-create',action='beneficiary')
 try:start=normalize_jalali(request.POST.get('start_date','')) if request.POST.get('start_date','') else '';end=normalize_jalali(request.POST.get('end_date','')) if request.POST.get('end_date','') else ''
 except ValueError:messages.error(request,'تاریخ رابطه معتبر نیست.');return redirect(f"{reverse('operation-create',kwargs={'action':'beneficiary'})}?space={space.code}")
 with transaction.atomic():
  beneficiary=Beneficiary.objects.create(name=name,kind=kind,identity_number=request.POST.get('identity_number','').strip(),contact=request.POST.get('contact','').strip())
  assignment=BeneficiaryAssignment.objects.create(space=space,beneficiary=beneficiary,role=request.POST.get('role','').strip(),start_date=start,end_date=end,status='ACTIVE',created_by=request.user)
  AuditEvent.objects.create(actor=request.user,action='BENEFICIARY_CREATE',entity_type='Beneficiary',entity_id=str(beneficiary.pk),after={'space':space.code,'kind':kind},ip_address=request.META.get('REMOTE_ADDR'))
  TimelineEvent.objects.create(space=space,event_type='BENEFICIARY_CREATE',jalali_date=start,source_entity='BeneficiaryAssignment',source_entity_id=str(assignment.pk),title=f'ثبت بهره‌بردار: {name}',new_state='ACTIVE',responsible_person=request.user.get_full_name() or request.user.username,provenance='ثبت عملیاتی')
 messages.success(request,'بهره‌بردار و ارتباط پرونده ثبت شد.');return redirect('space-detail',code=space.code)

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
 try:create_alert(space=space,actor=request.user,subject=request.POST.get('subject',''),reason=request.POST.get('reason',''),due_date=request.POST.get('due_date',''),priority=request.POST.get('priority','MEDIUM'),ip_address=request.META.get('REMOTE_ADDR'))
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
 target=get_object_or_404(get_user_model(),pk=user_id)
 if is_fixed_uat_admin(target):messages.error(request,'بازنشانی گذرواژه مدیر ثابت UAT مجاز نیست.');return redirect('user-list')
 temporary=secrets.token_urlsafe(18);target.set_password(temporary);target.save(update_fields=['password']); profile,_=UserProfile.objects.get_or_create(user=target,defaults={'display_name':target.get_full_name() or target.username});profile.must_change_password=True;profile.save(update_fields=['must_change_password'])
 AuditEvent.objects.create(actor=request.user,action='USER_PASSWORD_RESET',entity_type='User',entity_id=str(target.pk),reason=request.POST.get('reason','بازنشانی مدیریتی').strip(),after={'must_change_password':True},ip_address=request.META.get('REMOTE_ADDR'))
 messages.success(request,f'گذرواژه موقت {target.username} فقط همین بار: {temporary}');return redirect('user-list')

@login_required
@user_passes_test(lambda u:u.is_staff)
@require_POST
def user_toggle_active(request,user_id):
 from django.contrib.auth import get_user_model
 from domains.identity.models import AuditEvent
 target=get_object_or_404(get_user_model(),pk=user_id)
 if is_fixed_uat_admin(target):messages.error(request,'مدیر ثابت UAT باید فعال باقی بماند.');return redirect('user-list')
 if target==request.user:
  messages.error(request,'مدیر نمی‌تواند حساب جاری خود را غیرفعال کند.');return redirect('user-list')
 before=target.is_active;target.is_active=not before;target.save(update_fields=['is_active']);AuditEvent.objects.create(actor=request.user,action='USER_STATUS_CHANGE',entity_type='User',entity_id=str(target.pk),reason=request.POST.get('reason','تغییر وضعیت دسترسی').strip(),before={'active':before},after={'active':target.is_active},ip_address=request.META.get('REMOTE_ADDR'));messages.success(request,'وضعیت کاربر تغییر کرد.');return redirect('user-list')

@login_required
def contract_circulation_workspace(request):
 from domains.contracts.models import ContractCirculation
 cases=ContractCirculation.objects.select_related('space','beneficiary','official_contract').prefetch_related('transfers','signature_steps').order_by('-pk')
 code=request.GET.get('space','').strip()
 if code:cases=cases.filter(space__code=code)
 if request.GET.get('beneficiary'):cases=cases.filter(beneficiary__name__icontains=request.GET['beneficiary'])
 if request.GET.get('state'):cases=cases.filter(state=request.GET['state'])
 if request.GET.get('holder'):cases=cases.filter(transfers__returned_at__isnull=True,transfers__receiver__icontains=request.GET['holder'])
 if request.GET.get('unit'):cases=cases.filter(transfers__returned_at__isnull=True,transfers__unit__icontains=request.GET['unit'])
 if request.GET.get('ready')=='1':cases=cases.filter(state='READY_APPROVAL')
 return render(request,'ui/contract_circulation.html',{'cases':cases.distinct()[:100],'selected_space':CommercialSpace.objects.filter(code=code).first(),'spaces':filter_spaces({}),'beneficiaries':Beneficiary.objects.order_by('name')[:1000],'states':__import__('domains.contracts.models',fromlist=['ContractCirculation']).ContractCirculation.State.choices})

@login_required
@require_POST
def contract_circulation_create(request):
 from django.core.exceptions import ValidationError
 from services.contract_circulation import create_circulation
 space=get_object_or_404(CommercialSpace,code=request.POST.get('space_code'));beneficiary=get_object_or_404(Beneficiary,pk=request.POST.get('beneficiary'))
 try:create_circulation(space=space,beneficiary=beneficiary,subject=request.POST.get('subject','').strip(),operational_start_date=request.POST.get('operational_start_date',''),next_action=request.POST.get('next_action','').strip(),due_date=request.POST.get('due_date',''),actor=request.user)
 except ValidationError as exc:messages.error(request,' '.join(exc.messages))
 else:messages.success(request,'پرونده گردش قرارداد ثبت شد؛ این پرونده هنوز قرارداد رسمی نیست.')
 return redirect(reverse('contract-circulation')+f'?space={space.code}')

@login_required
@require_POST
def contract_transfer(request,case_id):
 from django.core.exceptions import ValidationError
 from django.utils.dateparse import parse_datetime
 from services.contract_circulation import transfer
 case=get_object_or_404(__import__('domains.contracts.models',fromlist=['ContractCirculation']).ContractCirculation,pk=case_id)
 try:transfer(circulation=case,sender=request.POST.get('sender',''),receiver=request.POST.get('receiver',''),unit=request.POST.get('unit',''),purpose=request.POST.get('purpose',''),next_action=request.POST.get('next_action',''),delivered_at=parse_datetime(request.POST.get('delivered_at','')) or __import__('django.utils.timezone',fromlist=['now']).now(),due_date=request.POST.get('due_date',''),actor=request.user)
 except ValidationError as exc:messages.error(request,' '.join(exc.messages))
 return redirect(reverse('contract-circulation')+f'?space={case.space.code}')

@login_required
@require_POST
def contract_return(request,case_id):
 from django.core.exceptions import ValidationError
 from services.contract_circulation import return_custody
 case=get_object_or_404(__import__('domains.contracts.models',fromlist=['ContractCirculation']).ContractCirculation,pk=case_id)
 try:return_custody(circulation=case,actor=request.user,note=request.POST.get('note',''))
 except ValidationError as exc:messages.error(request,' '.join(exc.messages))
 return redirect(reverse('contract-circulation')+f'?space={case.space.code}')
