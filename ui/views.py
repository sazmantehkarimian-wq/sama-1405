from django.contrib.auth.decorators import login_required,user_passes_test
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.core.paginator import Paginator
from django.http import HttpResponse, FileResponse
from django.shortcuts import render,get_object_or_404,redirect
from django.db.models import Count, OuterRef, Q, Subquery, Sum
from django.utils import timezone
from domains.properties.models import CommercialSpace,Region,Center,MotherProperty
from domains.registry.models import Discrepancy
from domains.identity.models import AuditEvent, UserProfile, SavedFilter, SavedReport, ArchivedReportSnapshot
from domains.contracts.models import Contract, Beneficiary
from domains.operations.models import Appraiser, Appraisal, AppraisalFee, Auction, AuctionEvaluation, AuctionPeriod, AuctionRule, CommissionDecision, ExpertFeePaymentBatch, UtilityBill, UtilityConnection, UtilityMeasurement, UtilityRecord, UtilityObligation, FileMovement, WorkflowInstance, Alert, DecisionOrder
from domains.documents.models import Document
from queries.spaces import filter_spaces
from services.file_movement import current_holder
from reporting.engine import excel,docx,pdf,tabular_excel,tabular_pdf,multi_sheet_excel,multi_section_pdf
from ui.forms import PersianPasswordChangeForm
from core.uat import is_fixed_uat_admin
from services.money import format_rial
def _filtered_utility_bills(params):
 from decimal import Decimal, InvalidOperation
 previous=UtilityBill.objects.filter(
  connection=OuterRef('connection_id'),
  period_end__lt=OuterRef('period_start'),
 ).order_by('-period_end','-pk')
 qs=UtilityBill.objects.select_related(
  'connection','connection__space','connection__space__region','connection__space__center','measurement','supporting_document'
 ).annotate(
  previous_amount_rial=Subquery(previous.values('amount_rial')[:1]),
  previous_consumption=Subquery(previous.values('consumption')[:1]),
 ).order_by('-period_end','-pk')
 q=(params.get('q') or '').strip()
 if q:
  qs=qs.filter(
   Q(connection__space__code__iexact=q)
   |Q(connection__space__name__icontains=q)
   |Q(connection__account_number__icontains=q)
   |Q(connection__meter_number__icontains=q)
   |Q(connection__provider__icontains=q)
  )
 utility_type=(params.get('utility_type') or '').strip()
 if utility_type in UtilityConnection.Type.values:qs=qs.filter(connection__utility_type=utility_type)
 payment=(params.get('payment_status') or '').strip()
 if payment in UtilityBill.PaymentStatus.values:qs=qs.filter(payment_status=payment)
 region=(params.get('region') or '').strip()
 if region.isdigit():qs=qs.filter(connection__space__region_id=region)
 center=(params.get('center') or '').strip()
 if center.isdigit():qs=qs.filter(connection__space__center_id=center)
 period_from=(params.get('period_from') or '').strip()
 period_to=(params.get('period_to') or '').strip()
 if period_from:qs=qs.filter(period_end__gte=period_from)
 if period_to:qs=qs.filter(period_start__lte=period_to)
 presence=(params.get('measurement') or '').strip()
 if presence=='yes':qs=qs.filter(measurement__isnull=False)
 elif presence=='no':qs=qs.filter(measurement__isnull=True)
 try:
  if params.get('amount_min'):qs=qs.filter(amount_rial__gte=Decimal(str(params.get('amount_min')).replace(',','')))
  if params.get('amount_max'):qs=qs.filter(amount_rial__lte=Decimal(str(params.get('amount_max')).replace(',','')))
 except (InvalidOperation,ValueError):
  return qs.none()
 return qs


@login_required
def utility_dashboard(request):
 qs=_filtered_utility_bills(request.GET)
 page=Paginator(qs,50).get_page(request.GET.get('page'))
 for item in page.object_list:
  item.amount_change_rial=(item.amount_rial-item.previous_amount_rial) if item.previous_amount_rial is not None else None
  item.consumption_change=(item.consumption-item.previous_consumption) if item.consumption is not None and item.previous_consumption is not None else None
 totals=qs.aggregate(total_amount=Sum('amount_rial'),total_consumption=Sum('consumption'))
 context={
  'page':page,
  'bill_count':qs.count(),
  'connection_count':qs.values('connection_id').distinct().count(),
  'total_amount':totals['total_amount'] or 0,
  'total_consumption':totals['total_consumption'],
  'water_count':qs.filter(connection__utility_type=UtilityConnection.Type.WATER).count(),
  'gas_count':qs.filter(connection__utility_type=UtilityConnection.Type.GAS).count(),
  'measurement_count':qs.filter(measurement__isnull=False).count(),
  'regions':Region.objects.order_by('name'),
  'centers':Center.objects.order_by('name'),
  'utility_types':UtilityConnection.Type.choices,
  'payment_statuses':UtilityBill.PaymentStatus.choices,
 }
 return render(request,'ui/utility_dashboard.html',context)


@login_required
def utility_bills_excel(request):
 qs=_filtered_utility_bills(request.GET)
 labels=['کد قبض','نوع انشعاب','کد فضا','نام فضا','منطقه','مرکز','شماره اشتراک','شماره کنتور','شروع دوره','پایان دوره','تاریخ قبض','مبلغ قبض (ریال)','مصرف','وضعیت پرداخت','تاریخ پرداخت','Measurement','سند قبض']
 def data():
  for item in qs[:10000]:
   yield [
    item.sama_code,item.connection.get_utility_type_display(),item.connection.space.code,item.connection.space.name or '—',
    item.connection.space.region.name if item.connection.space.region else '—',
    item.connection.space.center.name if item.connection.space.center else '—',
    item.connection.account_number,item.connection.meter_number or '—',item.period_start,item.period_end,item.bill_date or '—',
    item.amount_rial,item.consumption if item.consumption is not None else '—',item.get_payment_status_display(),item.payment_date or '—',
    f'{item.measurement.consumption} {item.measurement.measurement_unit}' if item.measurement_id else '—',
    item.supporting_document.title if item.supporting_document_id else '—',
   ]
 return HttpResponse(
  tabular_excel('قبوض آب و گاز',labels,data()),
  content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
  headers={'Content-Disposition':'attachment; filename="utility-bills.xlsx"'},
 )


@login_required
def utility_bills_pdf(request):
 qs=_filtered_utility_bills(request.GET)
 labels=['نوع انشعاب','کد فضا','شماره اشتراک','دوره','مبلغ قبض (ریال)','مصرف','وضعیت پرداخت','Measurement']
 def data():
  for item in qs[:5000]:
   yield [
    item.connection.get_utility_type_display(),item.connection.space.code,item.connection.account_number,
    f'{item.period_start} تا {item.period_end}',item.amount_rial,
    item.consumption if item.consumption is not None else '—',item.get_payment_status_display(),
    f'{item.measurement.consumption} {item.measurement.measurement_unit}' if item.measurement_id else '—',
   ]
 return HttpResponse(
  tabular_pdf('گزارش قبوض آب، گاز و سایر انشعابات',labels,data()),
  content_type='application/pdf',
  headers={'Content-Disposition':'attachment; filename="utility-bills.pdf"'},
 )


def _filtered_expert_fees(params):
 qs=AppraisalFee.objects.select_related(
  'appraisal','appraisal__space','appraisal__space__region','appraisal__appraiser_ref','supporting_document'
 ).prefetch_related('batch_items__batch').order_by('-created_at','-pk')
 q=(params.get('q') or '').strip()
 if q:
  condition=(
   Q(appraisal__space__code__iexact=q)
   |Q(appraisal__space__name__icontains=q)
   |Q(appraisal__appraiser__icontains=q)
   |Q(appraisal__appraiser_ref__first_name__icontains=q)
   |Q(appraisal__appraiser_ref__last_name__icontains=q)
   |Q(letter_number__icontains=q)
   |Q(payment_reference__icontains=q)
  )
  pk=_system_pk(q,'FEE')
  if pk:condition|=Q(pk=pk)
  qs=qs.filter(condition)
 status=(params.get('status') or '').strip()
 if status in AppraisalFee.Status.values:qs=qs.filter(status=status)
 region=(params.get('region') or '').strip()
 if region.isdigit():qs=qs.filter(appraisal__space__region_id=region)
 appraisal_from=(params.get('appraisal_from') or '').strip()
 appraisal_to=(params.get('appraisal_to') or '').strip()
 if appraisal_from:qs=qs.filter(appraisal__appraisal_date__gte=appraisal_from)
 if appraisal_to:qs=qs.filter(appraisal__appraisal_date__lte=appraisal_to)
 sent_from=(params.get('sent_from') or '').strip()
 sent_to=(params.get('sent_to') or '').strip()
 if sent_from:qs=qs.filter(sent_to_finance_date__gte=sent_from)
 if sent_to:qs=qs.filter(sent_to_finance_date__lte=sent_to)
 paid_from=(params.get('paid_from') or '').strip()
 paid_to=(params.get('paid_to') or '').strip()
 if paid_from:qs=qs.filter(payment_date__gte=paid_from)
 if paid_to:qs=qs.filter(payment_date__lte=paid_to)
 batch=(params.get('batch') or '').strip()
 if batch:qs=qs.filter(batch_items__active=True,batch_items__batch__code__icontains=batch)
 payment=(params.get('payment') or '').strip()
 if payment=='paid':qs=qs.filter(status__in=[AppraisalFee.Status.PAID,AppraisalFee.Status.CLOSED])
 elif payment=='unpaid':qs=qs.exclude(status__in=[AppraisalFee.Status.PAID,AppraisalFee.Status.CLOSED])
 return qs.distinct()


@login_required
def expert_fee_dashboard(request):
 qs=_filtered_expert_fees(request.GET)
 page=Paginator(qs,50).get_page(request.GET.get('page'))
 totals=qs.aggregate(total_amount=Sum('amount_rial'),paid_amount=Sum('paid_amount_rial'))
 total_amount=totals['total_amount'] or 0
 paid_amount=totals['paid_amount'] or 0
 missing_fees=Appraisal.objects.filter(appraiser_ref__isnull=False,fee__isnull=True).select_related('space','space__region','appraiser_ref').order_by('-appraisal_date','-pk')
 context={
  'page':page,
  'fee_count':qs.count(),
  'missing_fee_count':missing_fees.count(),
  'missing_fees':missing_fees[:100],
  'entered_count':qs.filter(status=AppraisalFee.Status.FEE_ENTERED).count(),
  'ready_count':qs.filter(status=AppraisalFee.Status.READY_TO_SEND).count(),
  'sent_count':qs.filter(status=AppraisalFee.Status.SENT_TO_FINANCE).count(),
  'progress_count':qs.filter(status=AppraisalFee.Status.IN_PROGRESS).count(),
  'paid_count':qs.filter(status__in=[AppraisalFee.Status.PAID,AppraisalFee.Status.CLOSED]).count(),
  'correction_count':qs.filter(status=AppraisalFee.Status.NEEDS_CORRECTION).count(),
  'total_amount':total_amount,'paid_amount':paid_amount,'pending_amount':total_amount-paid_amount,
  'statuses':AppraisalFee.Status.choices,'regions':Region.objects.order_by('name'),
  'batches':ExpertFeePaymentBatch.objects.prefetch_related('items__fee').order_by('-created_at','-pk')[:30],
 }
 return render(request,'ui/expert_fee_dashboard.html',context)


@login_required
def expert_fees_excel(request):
 qs=_filtered_expert_fees(request.GET)
 labels=[
  'کد حق‌الزحمه','کد کارشناسی','کد فضا','نام فضا','منطقه','کارشناس','کد کارشناس',
  'تاریخ کارشناسی','مبلغ کارشناسی (ریال)','مبلغ حق‌الزحمه (ریال)','وضعیت',
  'تاریخ ارسال به مالی','شماره نامه / گردش','تاریخ نامه / گردش',
  'تاریخ پرداخت','مبلغ پرداخت‌شده (ریال)','مرجع پرداخت','Batch',
 ]
 def data():
  for item in qs[:10000]:
   active_batch=next((x.batch for x in item.batch_items.all() if x.active),None)
   expert=item.appraisal.appraiser_ref
   yield [
    item.sama_code,item.appraisal.sama_code,item.appraisal.space.code,item.appraisal.space.name or '—',
    item.appraisal.space.region.name if item.appraisal.space.region else '—',
    item.appraisal.appraiser_display,expert.sama_code if expert else '—',
    item.appraisal.appraisal_date or '—',item.appraisal.amount_rial if item.appraisal.amount_rial is not None else '—',
    item.amount_rial,item.get_status_display(),item.sent_to_finance_date or '—',item.letter_number or '—',
    item.letter_date or '—',item.payment_date or '—',
    item.paid_amount_rial if item.paid_amount_rial is not None else '—',item.payment_reference or '—',
    active_batch.sama_code if active_batch else '—',
   ]
 return HttpResponse(
  tabular_excel('حق‌الزحمه کارشناسان',labels,data()),
  content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
  headers={'Content-Disposition':'attachment; filename="expert-fees.xlsx"'},
 )


@login_required
def expert_fees_pdf(request):
 qs=_filtered_expert_fees(request.GET)
 labels=['کد حق‌الزحمه','کد کارشناسی','کد فضا','کارشناس','مبلغ حق‌الزحمه (ریال)','وضعیت','ارسال به مالی','شماره نامه / گردش','تاریخ پرداخت','مبلغ پرداخت‌شده (ریال)','مرجع پرداخت']
 def data():
  for item in qs[:5000]:
   yield [
    item.sama_code,item.appraisal.sama_code,item.appraisal.space.code,item.appraisal.appraiser_display,
    item.amount_rial,item.get_status_display(),item.sent_to_finance_date or '—',item.letter_number or '—',
    item.payment_date or '—',item.paid_amount_rial if item.paid_amount_rial is not None else '—',
    item.payment_reference or '—',
   ]
 return HttpResponse(
  tabular_pdf('گزارش حق‌الزحمه کارشناسان',labels,data()),
  content_type='application/pdf',
  headers={'Content-Disposition':'attachment; filename="expert-fees.pdf"'},
 )


@login_required
def dashboard(request):
 spaces=CommercialSpace.objects.all()
 active=spaces.filter(status='ACTIVE')
 active_scope=filter_spaces({'status':['ACTIVE']})
 region_rows=list(active.exclude(region=None).values('region__name').annotate(total=Count('id')).order_by('-total')[:5])
 maximum=max((row['total'] for row in region_rows),default=1)
 for row in region_rows:row['percent']=round(row['total']*100/maximum)

 current_contract_count=filter_spaces({'status':['ACTIVE'],'current_contract':'present'}).count()
 without_current_contract_count=filter_spaces({'status':['ACTIVE'],'current_contract':'empty'}).count()
 current_appraisal_count=filter_spaces({'status':['ACTIVE'],'current_appraisal':'present'}).count()
 without_current_appraisal_count=filter_spaces({'status':['ACTIVE'],'current_appraisal':'empty'}).count()
 contract_today_count=filter_spaces({'status':['ACTIVE'],'contract_bucket':'TODAY'}).count()
 contract_1_30_count=filter_spaces({'status':['ACTIVE'],'contract_bucket':'1_30'}).count()
 contract_31_60_count=filter_spaces({'status':['ACTIVE'],'contract_bucket':'31_60'}).count()
 contract_61_90_count=filter_spaces({'status':['ACTIVE'],'contract_bucket':'61_90'}).count()
 long_term_contract_count=filter_spaces({'status':['ACTIVE'],'contract_bucket':'LONG_TERM'}).count()
 with_beneficiary_count=active_scope.filter(current_beneficiary_name__isnull=False).count()
 without_beneficiary_count=active_scope.filter(current_beneficiary_name__isnull=True).count()

 latest_by_space={}
 for item in AuctionEvaluation.objects.select_related('space').order_by('space_id','-evaluated_at','-pk'):
  if item.space_id not in latest_by_space:latest_by_space[item.space_id]=item
 latest_evaluations=[item for item in latest_by_space.values() if item.space.status=='ACTIVE']
 auction_candidate_count=sum(1 for item in latest_evaluations if item.decision=='CANDIDATE')
 auction_review_count=sum(1 for item in latest_evaluations if item.decision=='REVIEW_REQUIRED')
 auction_action_count=sum(1 for item in latest_evaluations if item.readiness=='ACTION_REQUIRED')

 context={
  'space_count':spaces.count(),'active_count':active.count(),'inactive_count':spaces.filter(status='OUT_OF_CYCLE').count(),
  'property_count':MotherProperty.objects.count(),'discrepancy_count':Discrepancy.objects.exclude(status='RESOLVED').count(),
  'contract_count':Contract.objects.count(),'appraisal_count':Appraisal.objects.count(),
  'alert_count':Alert.objects.exclude(status='RESOLVED').count(),
  'open_workflow_count':WorkflowInstance.objects.filter(state='OPEN').count(),
  'current_contract_count':current_contract_count,'without_contract_count':without_current_contract_count,
  'current_appraisal_count':current_appraisal_count,'without_appraisal_count':without_current_appraisal_count,
  'contract_today_count':contract_today_count,'contract_1_30_count':contract_1_30_count,
  'contract_31_60_count':contract_31_60_count,'contract_61_90_count':contract_61_90_count,
  'long_term_contract_count':long_term_contract_count,
  'with_beneficiary_count':with_beneficiary_count,'without_beneficiary_count':without_beneficiary_count,
  'auction_candidate_count':auction_candidate_count,'auction_review_count':auction_review_count,'auction_action_count':auction_action_count,
  'region_rows':region_rows,
  'refreshed_at':timezone.now(),
 }
 return render(request,'ui/dashboard.html',context)

@login_required
def mother_property_excel(request, pk):
 item=get_object_or_404(MotherProperty.objects.select_related('region'),pk=pk)
 from services.mother_property_reports import build_mother_property_sections
 sections=build_mother_property_sections(item)
 AuditEvent.objects.create(
  actor=request.user,action='MOTHER_PROPERTY_REPORT_EXPORT',entity_type='MotherProperty',entity_id=item.identifier,
  after={'format':'XLSX','section_count':len(sections)},ip_address=request.META.get('REMOTE_ADDR'),
 )
 payload=multi_sheet_excel(f'پرونده ملک مادر {item.identifier}',sections)
 return HttpResponse(payload,content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',headers={'Content-Disposition':f'attachment; filename="mother-property-{item.identifier}.xlsx"'})

@login_required
def mother_property_pdf(request, pk):
 item=get_object_or_404(MotherProperty.objects.select_related('region'),pk=pk)
 from services.mother_property_reports import build_mother_property_sections
 sections=build_mother_property_sections(item)
 AuditEvent.objects.create(
  actor=request.user,action='MOTHER_PROPERTY_REPORT_EXPORT',entity_type='MotherProperty',entity_id=item.identifier,
  after={'format':'PDF','section_count':len(sections)},ip_address=request.META.get('REMOTE_ADDR'),
 )
 payload=multi_section_pdf(f'پرونده ملک مادر {item.identifier}',sections)
 return HttpResponse(payload,content_type='application/pdf',headers={'Content-Disposition':f'attachment; filename="mother-property-{item.identifier}.pdf"'})

@login_required
def global_search(request):
 q=(request.GET.get('q') or '').strip()
 spaces=CommercialSpace.objects.none()
 contracts=Contract.objects.none()
 beneficiaries=Beneficiary.objects.none()
 appraisers=Appraiser.objects.none()
 if q:
  spaces=CommercialSpace.objects.select_related('region','center').filter(
   Q(code__iexact=q)|Q(name__icontains=q)
  ).order_by('code')[:20]
  contracts=Contract.objects.select_related('space','beneficiary').filter(
   Q(number__icontains=q)|Q(space__code__iexact=q)|Q(beneficiary__name__icontains=q)
  ).order_by('-start_date','-pk')[:20]
  beneficiaries=Beneficiary.objects.filter(
   Q(name__icontains=q)|Q(identity_number__iexact=q)
  ).order_by('name','pk')[:20]
  appraisers=Appraiser.objects.filter(
   Q(first_name__icontains=q)|Q(last_name__icontains=q)|Q(national_id__iexact=q)|
   Q(license_number__icontains=q)|Q(specialty__icontains=q)
  ).order_by('last_name','first_name','pk')[:20]
 return render(request,'ui/global_search.html',{
  'q':q,'spaces':spaces,'contracts':contracts,'beneficiaries':beneficiaries,'appraisers':appraisers,
  'result_count':len(spaces)+len(contracts)+len(beneficiaries)+len(appraisers) if q else 0,
 })

@login_required
def space_list(request,status_scope=None):
 qs=filter_spaces(request.GET)
 if status_scope in CommercialSpace.Status.values: qs=qs.filter(status=status_scope)
 page=Paginator(qs,25).get_page(request.GET.get('page'))
 allowed_columns={'name','status','region','usage','area','beneficiary','contract','contract_end'}
 requested=set(request.GET.getlist('column')) & allowed_columns
 visible=requested or allowed_columns
 opposite=None
 candidate=(request.GET.get('code') or request.GET.get('q') or '').strip()
 if status_scope and candidate.isdigit() and not qs.filter(code=candidate).exists():
  opposite=CommercialSpace.objects.filter(code=candidate).exclude(status=status_scope).first()
 title='فضاهای تجاری'
 if status_scope=='ACTIVE': title='فضاهای تجاری فعال'
 elif status_scope=='OUT_OF_CYCLE': title='فضاهای تجاری از دور خارج‌شده'
 return render(request,'ui/space_list.html',{'page':page,'regions':Region.objects.all(),'centers':Center.objects.filter(is_special=True),'total':qs.count(),'dataset_total':CommercialSpace.objects.filter(status=status_scope).count() if status_scope else CommercialSpace.objects.count(),'saved_filters':SavedFilter.objects.filter(owner=request.user,domain='spaces'),'visible_columns':visible,'status_scope':status_scope,'page_title':title,'opposite_space':opposite})
@login_required
def space_detail(request,code):
 s=get_object_or_404(CommercialSpace.objects.select_related('region','center').prefetch_related('status_history','contracts__amendments','contracts__beneficiary','beneficiary_assignments__beneficiary','appraisals__fee__supporting_document','auctions','utilities__supporting_document','utility_obligations','utility_measurements','utility_connections__bills','electricity_allocations__bill__unit','decisions','commission_decisions__spaces','commission_cases__session','commission_cases__decisions__responsible','timeline__document','alerts__assigned_to','file_movements','workflows','source_documents'),code=code)
 timeline=s.timeline.all();event_type=request.GET.get('event_type','').strip()
 if event_type:timeline=timeline.filter(event_type=event_type)
 event_types=s.timeline.order_by().values_list('event_type',flat=True).distinct()
 documents=Document.objects.filter(entity_type='CommercialSpace',entity_id=s.code).order_by('-uploaded_at','-pk')
 return render(request,'ui/space_detail.html',{'space':s,'holder':current_holder(s),'timeline_events':timeline,'event_types':event_types,'uploaded_documents':documents.filter(archived_at__isnull=True),'document_history':documents,'history':__import__('domains.operations.models',fromlist=['OperationalHistory']).OperationalHistory.objects.filter(entity_type__in=['WorkflowInstance','AppraisalFee','UtilityRecord','CommissionDecision','Alert'])[:100]})

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
 'properties':('املاک مادر',MotherProperty.objects.select_related('region'),(('identifier','شناسه ملک'),('name','نام'),('current_status','وضعیت جاری'),('region.name','منطقه'),('primary_usage','کاربری'),('area','مساحت اعیان'),('ownership_document_status','وضعیت مالکیت'),('completeness_status','تکمیل پرونده'))),
 'discrepancies':('بررسی مغایرت‌های داده',Discrepancy.objects.select_related('assigned_to'),(('entity_key','شناسه رکورد'),('field_key','فیلد'),('observed_value','مقدار موجود'),('expected_value','مقدار مورد انتظار'),('reason','علت'),('severity','اهمیت'),('status','وضعیت'))),
 'contracts':('قراردادها',Contract.objects.select_related('space','beneficiary'),(('number','شماره'),('space.code','کد فضا'),('beneficiary.name','بهره‌بردار'),('start_date','شروع'),('end_date','پایان'),('time_status_label','وضعیت زمانی'),('remaining_days','روزهای باقی‌مانده'),('amount_rial','مبلغ (ریال)'),('status','وضعیت حقوقی'))),
 'beneficiaries':('بهره‌برداران',Beneficiary.objects.all(),(('sama_code','کد بهره‌بردار'),('name','نام / عنوان'),('identity_number','کد ملی / شناسه ملی'),('kind','نوع'),('completeness_status','وضعیت تکمیل'))),
 'appraisers':('کارشناسان',Appraiser.objects.all(),(('sama_code','کد کارشناس'),('full_name','نام کارشناس'),('license_number','شماره پروانه'),('specialty','رشته / صلاحیت'),('collaboration_status','وضعیت همکاری'))),
 'appraisals':('کارشناسی',Appraisal.objects.select_related('space','appraiser_ref'),(('sama_code','کد کارشناسی'),('space.code','کد فضا'),('appraiser_display','کارشناس'),('response_number','شماره جواب'),('response_date','تاریخ جواب'),('appraisal_date','تاریخ کارشناسی'),('amount_rial','مبلغ (ریال)'),('status','وضعیت'))),
 'fees':('حق‌الزحمه کارشناسی',AppraisalFee.objects.select_related('appraisal__space','appraisal__appraiser_ref'),(('sama_code','کد حق‌الزحمه'),('appraisal.space.code','کد فضا'),('appraisal.appraiser_display','کارشناس'),('amount_rial','مبلغ (ریال)'),('status','وضعیت'),('sent_to_finance_date','ارسال به مالی'),('letter_number','شماره نامه'),('payment_date','تاریخ پرداخت'),('payment_reference','مرجع پرداخت'))),
 'auctions':('مزایده‌ها',Auction.objects.select_related('space'),(('space.code','کد فضا'),('year','سال'),('sequence','نوبت'),('stage','مرحله'),('result','نتیجه'))),
 'commissions':('کمیسیون معاملات',CommissionDecision.objects.all(),(('identity','شناسه'),('decision_date','تاریخ'),('subject','موضوع'),('decision','تصمیم'))),
 'utilities':('انشعابات و مصرف',UtilityRecord.objects.select_related('space'),(('space.code','کد فضا'),('utility_type','نوع'),('account_number','اشتراک'),('bill_amount_rial','مبلغ قبض (ریال)'),('payment_status','پرداخت'))),
 'workflows':('گردش پرونده',WorkflowInstance.objects.select_related('space'),(('space.code','کد فضا'),('title','فرایند'),('state','وضعیت'),('next_action','اقدام بعدی'),('due_date','مهلت'))),
 'alerts':('موارد نیازمند پیگیری',Alert.objects.select_related('space','assigned_to'),(('space.code','کد فضا'),('subject','موضوع'),('reason','علت'),('due_date','سررسید'),('priority','اولویت'),('status','وضعیت'),('assigned_to.username','مسئول پیگیری'))),
 'documents':('اسناد بارگذاری‌شده',Document.objects.all(),(('title','عنوان'),('document_type','نوع'),('reference','مرجع'),('document_date','تاریخ سند'),('status_label','وضعیت'),('original_filename','نام فایل'),('uploaded_at','زمان بارگذاری'))),
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
def _system_pk(query,prefix):
 value=query.strip().upper()
 if value.startswith(prefix):
  suffix=value[len(prefix):].lstrip('-')
  if suffix.isdigit():return int(suffix)
 return None

def _search_domain(qs,domain,q):
 if not q:return qs
 if domain=='properties':
  return qs.filter(
   Q(identifier__iexact=q)|Q(name__icontains=q)|Q(region__name__icontains=q)|
   Q(primary_usage__icontains=q)|Q(usage_group__icontains=q)|Q(address__icontains=q)|
   Q(owner_name__icontains=q)|Q(holder_unit__icontains=q)
  )
 if domain=='contracts':
  return qs.filter(Q(number__icontains=q)|Q(space__code__iexact=q)|Q(space__name__icontains=q)|Q(beneficiary__name__icontains=q)|Q(beneficiary__identity_number__iexact=q))
 if domain=='appraisers':
  condition=Q(first_name__icontains=q)|Q(last_name__icontains=q)|Q(national_id__iexact=q)|Q(license_number__icontains=q)|Q(specialty__icontains=q)
  pk=_system_pk(q,'EXP')
  if pk:condition|=Q(pk=pk)
  return qs.filter(condition)
 if domain=='appraisals':
  condition=Q(space__code__iexact=q)|Q(space__name__icontains=q)|Q(appraiser__icontains=q)|Q(appraiser_ref__first_name__icontains=q)|Q(appraiser_ref__last_name__icontains=q)|Q(response_number__icontains=q)|Q(notifications__number__icontains=q)
  pk=_system_pk(q,'APR')
  if pk:condition|=Q(pk=pk)
  return qs.filter(condition).distinct()
 if domain=='fees':
  condition=Q(appraisal__space__code__iexact=q)|Q(appraisal__space__name__icontains=q)|Q(appraisal__appraiser__icontains=q)|Q(letter_number__icontains=q)|Q(payment_reference__icontains=q)
  pk=_system_pk(q,'FEE')
  if pk:condition|=Q(pk=pk)
  return qs.filter(condition)
 if domain in {'auctions','utilities','workflows','alerts'}:
  return qs.filter(space__code__iexact=q)
 if domain=='beneficiaries':
  condition=Q(name__icontains=q)|Q(identity_number__iexact=q)
  pk=_system_pk(q,'B')
  if pk:condition|=Q(pk=pk)
  return qs.filter(condition)
 if domain=='documents':
  return qs.filter(
   Q(title__icontains=q)|Q(document_type__icontains=q)|Q(reference__icontains=q)|
   Q(document_date__icontains=q)|Q(original_filename__icontains=q)|Q(entity_id__icontains=q)
  )
 return qs
@login_required
def domain_list(request,domain):
 title,qs,columns=DOMAIN_LISTS[domain]
 dataset_count=qs.count()
 q=request.GET.get('q','').strip()
 qs=_search_domain(qs,domain,q)
 page=Paginator(qs.order_by('-pk'),30).get_page(request.GET.get('page'))
 rows=[{'object':obj,'values':[_value(obj,key) for key,_ in columns]} for obj in page]
 return render(request,'ui/domain_list.html',{'title':title,'headers':[label for _,label in columns],'rows':rows,'page':page,'domain':domain,'dataset_count':dataset_count,'has_filter':bool(q)})

@login_required
def domain_excel(request,domain):
 if domain not in DOMAIN_LISTS:return HttpResponse(status=404)
 title,qs,columns=DOMAIN_LISTS[domain]
 q=request.GET.get('q','').strip()
 qs=_search_domain(qs,domain,q)
 labels=[label for _,label in columns]
 data=([_value(item,key) for key,_ in columns] for item in qs.order_by('pk')[:10000])
 return HttpResponse(tabular_excel(title,labels,data),content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',headers={'Content-Disposition':f'attachment; filename="{domain}.xlsx"'})

@login_required
def document_download(request,document_id):
 document=get_object_or_404(Document,pk=document_id)
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
  'instructions':AuctionInstruction.objects.select_related('space','created_by','commission_decision').order_by('-effective_from','-id')[:100],
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
 from django.core.exceptions import PermissionDenied, ValidationError
 from services.auctions import add_evaluated_lot, add_manual_lot
 period=get_object_or_404(AuctionPeriod,pk=period_id)
 mode=request.POST.get('mode','EVALUATED')
 try:
  if mode=='MANUAL':
   space=get_object_or_404(CommercialSpace,code=request.POST.get('space_code','').strip())
   add_manual_lot(
    period=period,space=space,actor=request.user,
    reason=request.POST.get('reason',''),reference=request.POST.get('reference',''),
    ip_address=request.META.get('REMOTE_ADDR'),
   )
  else:
   evaluation=get_object_or_404(AuctionEvaluation,pk=request.POST.get('evaluation_id'))
   add_evaluated_lot(period=period,evaluation=evaluation,actor=request.user,ip_address=request.META.get('REMOTE_ADDR'))
 except PermissionDenied as exc:messages.error(request,str(exc))
 except ValidationError as exc:messages.error(request,' '.join(exc.messages))
 else:messages.success(request,'فضا به دوره مزایده افزوده شد.')
 return redirect('auction-workspace')

@login_required
def commission_workspace(request):
 sessions=CommissionSession.objects.prefetch_related('cases__decisions').annotate(
  topic_count=Count('cases',distinct=True),
  open_decision_count_row=Count('cases__decisions',filter=Q(cases__decisions__execution_status__in=[
   CommissionDecision.ExecutionStatus.ACTION_REQUIRED,
   CommissionDecision.ExecutionStatus.IN_PROGRESS,
   CommissionDecision.ExecutionStatus.REVIEW_REQUIRED,
  ]),distinct=True),
 ).order_by('-session_date','-id')
 q=request.GET.get('q','').strip()
 status=request.GET.get('status','').strip()
 if q:sessions=sessions.filter(Q(number__icontains=q)|Q(title__icontains=q)|Q(cases__title__icontains=q)|Q(cases__spaces__code__iexact=q)).distinct()
 if status in CommissionSession.Status.values:sessions=sessions.filter(status=status)
 decisions=CommissionDecision.objects.filter(case__isnull=False)
 open_statuses=[CommissionDecision.ExecutionStatus.ACTION_REQUIRED,CommissionDecision.ExecutionStatus.IN_PROGRESS,CommissionDecision.ExecutionStatus.REVIEW_REQUIRED]
 return render(request,'ui/commission_workspace.html',{
  'sessions':sessions[:100],
  'members':CommissionMember.objects.order_by('sign_order','name')[:100],
  'session_count':sessions.count(),
  'open_decision_count':decisions.filter(execution_status__in=open_statuses).count(),
  'overdue_followup_count':CommissionFollowUp.objects.filter(status__in=open_statuses,due_date__lt=__import__('services.dates',fromlist=['today_jalali']).today_jalali()).exclude(due_date='').count(),
  'status_choices':CommissionSession.Status.choices,
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
def space_scoped_report(request):
 from urllib.parse import urlencode
 from services.scoped_reports import SCOPED_DOMAINS, build_space_sections, normalize_domains
 code=(request.GET.get('code') or '').strip()
 full=request.GET.get('full')=='1'
 domains=normalize_domains(request.GET.getlist('domain'),full=full)
 space=None;sections=[];not_found=False
 if code:
  space=CommercialSpace.objects.select_related('region','center').filter(code=code).first()
  if space is None:
   not_found=True
  else:
   sections=build_space_sections(space,domains)
 pairs=[('code',code)]+[('domain',key) for key in domains]
 export_query=urlencode(pairs)
 return render(request,'ui/space_scoped_report.html',{
  'scoped_domains':SCOPED_DOMAINS,'selected_domains':domains,'space':space,
  'sections':sections,'not_found':not_found,'code':code,'full':full,'export_query':export_query,
 })

@login_required
def space_scoped_excel(request):
 from services.scoped_reports import build_space_sections, normalize_domains
 code=(request.GET.get('code') or '').strip()
 space=get_object_or_404(CommercialSpace.objects.select_related('region','center'),code=code)
 domains=normalize_domains(request.GET.getlist('domain'),full=request.GET.get('full')=='1')
 sections=build_space_sections(space,domains)
 AuditEvent.objects.create(
  actor=request.user,action='SCOPED_REPORT_EXPORT',entity_type='CommercialSpace',entity_id=space.code,
  after={'format':'XLSX','domains':domains},ip_address=request.META.get('REMOTE_ADDR'),
 )
 payload=multi_sheet_excel(f'پرونده کد فضا {space.code}',sections)
 return HttpResponse(payload,content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',headers={'Content-Disposition':f'attachment; filename="space-{space.code}.xlsx"'})

@login_required
def space_scoped_pdf(request):
 from services.scoped_reports import build_space_sections, normalize_domains
 code=(request.GET.get('code') or '').strip()
 space=get_object_or_404(CommercialSpace.objects.select_related('region','center'),code=code)
 domains=normalize_domains(request.GET.getlist('domain'),full=request.GET.get('full')=='1')
 sections=build_space_sections(space,domains)
 AuditEvent.objects.create(
  actor=request.user,action='SCOPED_REPORT_EXPORT',entity_type='CommercialSpace',entity_id=space.code,
  after={'format':'PDF','domains':domains},ip_address=request.META.get('REMOTE_ADDR'),
 )
 payload=multi_section_pdf(f'پرونده کد فضا {space.code}',sections)
 return HttpResponse(payload,content_type='application/pdf',headers={'Content-Disposition':f'attachment; filename="space-{space.code}.pdf"'})

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
 from django.core.exceptions import ValidationError
 from services.file_movement import register_handover
 space=get_object_or_404(CommercialSpace,code=code)
 try:
  register_handover(space=space,actor=request.user,values=request.POST,ip_address=request.META.get('REMOTE_ADDR'))
 except ValidationError as exc:
  messages.error(request,' '.join(exc.messages))
 else:
  messages.success(request,'تحویل فیزیکی پرونده ثبت شد و دارنده جاری به‌روزرسانی شد.')
 return redirect('space-detail',code=code)

@login_required
@require_POST
def return_movement(request,code):
 from django.core.exceptions import ValidationError
 from services.file_movement import close_current_movement
 space=get_object_or_404(CommercialSpace,code=code)
 try:
  close_current_movement(space=space,actor=request.user,reason=request.POST.get('reason',''),ip_address=request.META.get('REMOTE_ADDR'))
 except ValidationError as exc:
  messages.error(request,' '.join(exc.messages))
 else:
  messages.success(request,'بازگشت پرونده ثبت شد و دارنده جاری بسته شد.')
 return redirect('space-detail',code=code)

@login_required
@require_POST
def upload_document(request,code):
 from django.core.exceptions import ValidationError
 from django.contrib import messages
 from services.documents import store_document
 space=get_object_or_404(CommercialSpace,code=code);uploaded=request.FILES.get('file')
 if not uploaded:messages.error(request,'فایل انتخاب نشده است.');return redirect('space-detail',code=code)
 try:store_document(uploaded=uploaded,title=request.POST.get('title','').strip() or uploaded.name,document_type=request.POST.get('document_type','سایر').strip(),entity_type='CommercialSpace',entity_id=space.code,user=request.user,reference=request.POST.get('reference',''),document_date=request.POST.get('document_date',''),notes=request.POST.get('notes',''),ip_address=request.META.get('REMOTE_ADDR'))
 except ValidationError as exc:messages.error(request,' '.join(exc.messages))
 else:messages.success(request,'سند با ثبت checksum بارگذاری شد.')
 return redirect('space-detail',code=code)

@login_required
@require_POST
def archive_document_view(request,document_id):
 from django.core.exceptions import ValidationError
 from services.documents import archive_document
 document=get_object_or_404(Document,pk=document_id)
 try:
  archive_document(
   document=document,user=request.user,reason=request.POST.get('reason',''),
   ip_address=request.META.get('REMOTE_ADDR'),
  )
 except ValidationError as exc:
  messages.error(request,' '.join(exc.messages))
 else:
  messages.success(request,'سند بدون حذف فیزیکی بایگانی شد.')
 if document.entity_type=='CommercialSpace':
  return redirect('space-detail',code=document.entity_id)
 if document.entity_type=='MotherProperty':
  item=MotherProperty.objects.filter(identifier=document.entity_id).first()
  if item:return redirect('mother-property-detail',pk=item.pk)
 return redirect('domain-list',domain='documents')

@login_required
@require_POST
def add_contract(request,code):
 from django.core.exceptions import ValidationError
 from services.contracts import create_contract
 space=get_object_or_404(CommercialSpace,code=code)
 beneficiary=get_object_or_404(Beneficiary,pk=request.POST.get('beneficiary_id'),archived_at__isnull=True)
 try:create_contract(space=space,beneficiary=beneficiary,actor=request.user,values=request.POST,ip_address=request.META.get('REMOTE_ADDR'))
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
 appraiser=get_object_or_404(Appraiser,pk=request.POST.get('appraiser_id'),archived_at__isnull=True)
 try:create_appraisal(space=space,appraiser=appraiser,actor=request.user,values=request.POST,document=document,ip_address=request.META.get('REMOTE_ADDR'))
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
