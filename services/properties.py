from django.core.exceptions import ValidationError
from django.db import transaction

from domains.identity.models import AuditEvent
from domains.operations.models import TimelineEvent
from domains.properties.models import CommercialSpace, CommercialSpaceStatusHistory
from services.database import retry_locked
from services.dates import normalize_jalali


@retry_locked
@transaction.atomic
def transition_space_status(*,space,actor,new_state,effective_date,reason,document=None,ip_address=None):
 if new_state not in CommercialSpace.Status.values or new_state==space.status:
  raise ValidationError('وضعیت مقصد باید معتبر و متفاوت از وضعیت جاری باشد.')
 if not reason.strip():raise ValidationError('علت تغییر وضعیت الزامی است.')
 try:date=normalize_jalali(effective_date)
 except ValueError as exc:raise ValidationError('تاریخ اثر شمسی معتبر نیست.') from exc
 previous=space.status
 history=CommercialSpaceStatusHistory.objects.create(space=space,previous_state=previous,new_state=new_state,effective_date=date,reason=reason.strip(),responsible_user=actor,source_document=document)
 space.status=new_state;space.save(update_fields=['status'])
 AuditEvent.objects.create(actor=actor,action='SPACE_STATUS_TRANSITION',entity_type='CommercialSpace',entity_id=space.code,reason=reason.strip(),before={'status':previous},after={'status':new_state,'history':history.pk},ip_address=ip_address)
 TimelineEvent.objects.create(space=space,event_type='SPACE_STATUS_TRANSITION',jalali_date=date,source_entity='CommercialSpaceStatusHistory',source_entity_id=str(history.pk),title='تغییر وضعیت فضای تجاری',description=reason.strip(),previous_state=previous,new_state=new_state,responsible_person=actor.get_full_name() or actor.username,document=document,provenance='رویداد عملیاتی مصوب',target_url=f'/spaces/{space.code}/')
 return history
