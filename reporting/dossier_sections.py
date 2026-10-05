"""Central registry for exact Commercial Space dossier section datasets."""
from dataclasses import dataclass
from domains.documents.models import Document

@dataclass(frozen=True)
class SectionReport:
 key: str
 title: str
 labels: tuple
 rows: list

SECTIONS={
 'summary':'مشخصات پایه','beneficiaries':'بهره‌برداران و سوابق','contracts':'قراردادها و الحاقیه‌ها','appraisals':'کارشناسی و حق‌الزحمه','auctions':'مزایده، کمیسیون و مصوبات','utilities':'انشعابات، تعهدات و مصرف','workflow':'پیگیری پرونده و گردش فیزیکی','documents':'مدارک و مستندات','alerts':'موارد نیازمند پیگیری','timeline':'خط زمانی کامل پرونده',
}

def _display(obj, field, default='ثبت نشده'):
 method=getattr(obj,f'get_{field}_display',None);value=method() if method else getattr(obj,field,None)
 return value if value not in (None,'') else default

def section_report(space,key):
 if key not in SECTIONS:raise KeyError(key)
 titles={'beneficiaries':'سوابق بهره‌برداران','contracts':'سوابق قراردادهای','appraisals':'سوابق کارشناسی','utilities':'گزارش انشعابات و مصرف','workflow':'گزارش گردش پرونده','timeline':'خط زمانی کامل پرونده'}
 title=f"{titles.get(key,SECTIONS[key])} فضای تجاری {space.code}"
 if key=='summary':
  labels=('کد فضا','نام فضا / مرکز','منطقه','مرکز','وضعیت','کاربری','مساحت','نشانی')
  rows=[[space.code,space.name,_display(space.region,'name') if space.region else 'ثبت نشده',space.center.name if space.center else 'ثبت نشده',space.get_status_display(),space.current_usage or 'ثبت نشده',space.area if space.area is not None else 'ثبت نشده',space.address or 'ثبت نشده']]
 elif key=='beneficiaries':
  labels=('نام بهره‌بردار','شناسه','نوع','نقش','از تاریخ','تا تاریخ','وضعیت','ردیف منبع')
  rows=[[a.beneficiary.name,a.beneficiary.identity_number or 'ثبت نشده',a.beneficiary.get_kind_display(),a.role or 'ثبت نشده',a.start_date or 'ثبت نشده',a.end_date or 'ثبت نشده',a.status or 'ثبت نشده',a.source_row or 'ثبت عملیاتی'] for a in space.beneficiary_assignments.select_related('beneficiary').all()]
 elif key=='contracts':
  labels=('شماره قرارداد','بهره‌بردار','شروع','پایان','مبلغ (ریال)','وضعیت','نوع سابقه','ردیف منبع')
  rows=[[c.number or 'بدون شماره معتبر',c.beneficiary.name if c.beneficiary else 'ثبت نشده',c.start_date or 'ثبت نشده',c.end_date or 'ثبت نشده',c.amount_rial if c.amount_rial is not None else 'ثبت نشده',c.status or 'ثبت نشده','تاریخی' if c.is_historical else 'عملیاتی',c.source_row or 'ثبت عملیاتی'] for c in space.contracts.select_related('beneficiary').all()]
 elif key=='appraisals':
  labels=('سال','تاریخ','کارشناس','مبلغ (ریال)','وضعیت / کیفیت','حق‌الزحمه','ردیف منبع')
  rows=[[a.year or 'ثبت نشده',a.appraisal_date or 'ثبت نشده',a.appraiser or 'ثبت نشده',a.amount_rial if a.amount_rial is not None else 'نامشخص',a.status or ('کامل' if a.appraisal_date and a.appraiser and a.amount_rial is not None else 'ناقص'),a.fee.amount_rial if hasattr(a,'fee') else 'ثبت نشده',a.source_row or 'ثبت عملیاتی'] for a in space.appraisals.select_related('fee').all()]
 elif key=='auctions':
  labels=('نوع رکورد','تاریخ / سال','شناسه / موضوع','مرحله / تصمیم','نتیجه / شرح','ردیف منبع')
  rows=[["مزایده",a.year or 'ثبت نشده',a.sequence or 'ثبت نشده',a.stage or 'ثبت نشده',a.result or 'ثبت نشده',a.source_row] for a in space.auctions.all()]
  rows += [["کمیسیون",d.decision_date or 'ثبت نشده',d.subject,d.get_state_display(),d.decision,'ثبت عملیاتی'] for d in space.commission_decisions.all()]
  rows += [["مصوبه",d.decision_date or 'ثبت نشده',d.decision_type,d.review_status or 'ثبت نشده',d.text,d.source_row] for d in space.decisions.all()]
 elif key=='utilities':
  labels=('نوع','دوره / روش','مصرف','مبلغ کل (ریال)','سهم سازمان','سهم بهره‌بردار','وضعیت / توضیح')
  rows=[[_display(u,'utility_type'),f'{u.period_start} تا {u.period_end}',u.consumption if u.consumption is not None else 'نامشخص',u.bill_amount_rial,u.organization_share_rial,u.beneficiary_share_rial,u.payment_status] for u in space.utilities.all()]
  rows += [[u.utility_type,u.calculation_type or 'تعهد منبع','—',u.amount_rial if u.amount_rial is not None else 'نامشخص','—','—',u.notes or u.standard_description or 'ثبت نشده'] for u in space.utility_obligations.all()]
 elif key=='workflow':
  labels=('نوع رکورد','عنوان / محل','دارنده / وضعیت','تاریخ تحویل','تاریخ بازگشت','اقدام بعدی','مهلت')
  rows=[["فرایند",w.title,w.get_state_display(),w.created_at.strftime('%Y-%m-%d'),'—',w.next_action,w.due_date or 'ثبت نشده'] for w in space.workflows.all()]
  rows += [["گردش فیزیکی",m.location,m.holder,m.handover_at.strftime('%Y-%m-%d %H:%M'),m.returned_at.strftime('%Y-%m-%d %H:%M') if m.returned_at else 'باز',m.next_action or 'ثبت نشده',m.due_date or 'ثبت نشده'] for m in space.file_movements.all()]
 elif key=='documents':
  labels=('نوع سند','عنوان / مرجع','وضعیت','نام فایل','منبع / توضیح')
  rows=[[d.document_type,d.reference or 'بدون شماره',d.status or 'ثبت نشده','—',d.notes or d.source_path or 'ثبت نشده'] for d in space.source_documents.all()]
  rows += [[d.document_type,d.title,'بارگذاری‌شده',d.original_filename,'سند عملیاتی'] for d in Document.objects.filter(entity_type='CommercialSpace',entity_id=space.code,archived_at__isnull=True)]
 elif key=='alerts':
  labels=('موضوع','علت','تاریخ اثر','سررسید','اولویت','وضعیت','مسئول')
  rows=[[a.subject,a.reason,a.effective_date or 'ثبت نشده',a.due_date or 'ثبت نشده',a.get_priority_display(),a.status,a.assigned_to.get_username() if a.assigned_to else 'ثبت نشده'] for a in space.alerts.select_related('assigned_to').all()]
 else:
  labels=('تاریخ','نوع رویداد','خلاصه','منبع','جزئیات','وضعیت تطبیق')
  rows=[[e.jalali_date or 'فاقد تاریخ',e.event_type,e.title,e.source_entity,e.description or 'ثبت نشده','نیازمند تطبیق' if not e.jalali_date else 'ثبت‌شده'] for e in space.timeline.all()]
 return SectionReport(key,title,labels,rows)
