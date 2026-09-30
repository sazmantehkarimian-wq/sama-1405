from decimal import Decimal, InvalidOperation

from django.core.exceptions import ValidationError
from django.db import transaction

from domains.contracts.models import Beneficiary, BeneficiaryAssignment, Contract, ContractAmendment
from domains.identity.models import AuditEvent
from domains.operations.models import OperationalHistory, TimelineEvent
from services.database import retry_locked
from services.dates import normalize_jalali


def effective_contract(queryset,on_date):
 return queryset.filter(start_date__lte=on_date,end_date__gte=on_date).exclude(status__in=['باطل','فسخ‌شده']).order_by('-start_date').first()


def _money(value, label):
 if value in (None,''):return None
 try:amount=Decimal(str(value).replace(',',''))
 except InvalidOperation as exc:raise ValidationError(f'{label} باید عدد معتبر باشد.') from exc
 if amount<0:raise ValidationError(f'{label} نمی‌تواند منفی باشد.')
 return amount


@retry_locked
@transaction.atomic
def create_contract(*,space,actor,values,ip_address=None):
 number=values.get('number','').strip();beneficiary_name=values.get('beneficiary','').strip()
 if not number or not beneficiary_name:raise ValidationError('شماره قرارداد و بهره‌بردار الزامی است.')
 if Contract.objects.filter(number=number,space=space).exists():raise ValidationError('این شماره قرارداد برای فضا تکراری است.')
 try:
  signed=normalize_jalali(values.get('signed_date',''))
  start=normalize_jalali(values.get('start_date',''));end=normalize_jalali(values.get('end_date',''))
 except ValueError as exc:raise ValidationError('تاریخ قرارداد معتبر نیست.') from exc
 if not start or not end or start>end:raise ValidationError('بازه تاریخ قرارداد معتبر نیست.')
 beneficiary,_=Beneficiary.objects.get_or_create(name=beneficiary_name)
 record=Contract.objects.create(space=space,beneficiary=beneficiary,number=number,signed_date=signed,start_date=start,end_date=end,amount_rial=_money(values.get('amount_rial'),'مبلغ قرارداد'),investment_commitment_rial=_money(values.get('investment_commitment_rial'),'تعهد سرمایه‌گذاری'),status=values.get('status','').strip(),signed_state=values.get('signed_state','').strip(),is_historical=False,created_by=actor)
 BeneficiaryAssignment.objects.create(space=space,beneficiary=beneficiary,role='بهره‌بردار قرارداد',start_date=start,end_date=end,status='ACTIVE',created_by=actor)
 AuditEvent.objects.create(actor=actor,action='CONTRACT_CREATE',entity_type='Contract',entity_id=str(record.pk),after={'space':space.code,'number':number},ip_address=ip_address)
 OperationalHistory.objects.create(entity_type='Contract',entity_id=str(record.pk),action='CREATED',new_state={'status':record.status},responsible=actor)
 TimelineEvent.objects.create(space=space,event_type='CONTRACT_CREATE',jalali_date=signed or start,source_entity='Contract',source_entity_id=str(record.pk),title=f'ثبت قرارداد {number}',new_state=record.status,responsible_person=actor.get_full_name() or actor.username,provenance='عملیات پس از شروع بهره‌برداری',target_url=f'/spaces/{space.code}/')
 return record


@retry_locked
@transaction.atomic
def add_amendment(*,contract,actor,values,ip_address=None):
 number=values.get('number','').strip();description=values.get('description','').strip()
 if not number or not description:raise ValidationError('شماره و شرح الحاقیه الزامی است.')
 try:date=normalize_jalali(values.get('effective_date',''))
 except ValueError as exc:raise ValidationError('تاریخ الحاقیه معتبر نیست.') from exc
 item=ContractAmendment.objects.create(contract=contract,number=number,effective_date=date,description=description,amount_change_rial=_money(values.get('amount_change_rial'),'تغییر مبلغ'))
 AuditEvent.objects.create(actor=actor,action='CONTRACT_AMENDMENT_CREATE',entity_type='ContractAmendment',entity_id=str(item.pk),after={'contract':contract.pk,'number':number},ip_address=ip_address)
 TimelineEvent.objects.create(space=contract.space,event_type='CONTRACT_AMENDMENT',jalali_date=date,source_entity='ContractAmendment',source_entity_id=str(item.pk),title=f'الحاقیه {number}',description=description,responsible_person=actor.get_full_name() or actor.username,provenance='عملیات پس از شروع بهره‌برداری',target_url=f'/spaces/{contract.space.code}/')
 return item
