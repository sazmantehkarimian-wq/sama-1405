import hashlib
from pathlib import Path
from django.core.exceptions import ValidationError
from django.db import transaction
from domains.documents.models import Document
from domains.identity.models import AuditEvent
from services.dates import normalize_jalali

ALLOWED={'.pdf':'application/pdf','.docx':'application/vnd.openxmlformats-officedocument.wordprocessingml.document','.xlsx':'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet','.png':'image/png','.jpg':'image/jpeg','.jpeg':'image/jpeg'}
MAX_BYTES=10*1024*1024

@transaction.atomic
def store_document(*,uploaded,title,document_type,entity_type,entity_id,user,reference="",document_date="",notes="",ip_address=None):
 suffix=Path(uploaded.name).suffix.lower()
 if suffix not in ALLOWED:raise ValidationError('نوع فایل مجاز نیست.')
 if uploaded.size>MAX_BYTES:raise ValidationError('حجم فایل بیش از حد مجاز است.')
 try:normalized_date=normalize_jalali(document_date) if (document_date or "").strip() else ""
 except ValueError as exc:raise ValidationError('تاریخ سند معتبر نیست.') from exc
 digest=hashlib.sha256()
 for chunk in uploaded.chunks():digest.update(chunk)
 uploaded.seek(0)
 document=Document.objects.create(title=title,document_type=document_type,reference=(reference or "").strip(),document_date=normalized_date,notes=(notes or "").strip(),file=uploaded,original_filename=Path(uploaded.name).name,sha256=digest.hexdigest(),content_type=ALLOWED[suffix],byte_size=uploaded.size,entity_type=entity_type,entity_id=str(entity_id),uploaded_by=user)
 AuditEvent.objects.create(actor=user,action='DOCUMENT_UPLOAD',entity_type=entity_type,entity_id=str(entity_id),after={'document_id':document.pk,'sha256':document.sha256,'document_type':document.document_type,'reference':document.reference,'document_date':document.document_date},ip_address=ip_address)
 if entity_type=='CommercialSpace':
  from domains.operations.models import TimelineEvent
  from domains.properties.models import CommercialSpace
  space=CommercialSpace.objects.filter(code=str(entity_id)).first()
  if space:TimelineEvent.objects.create(space=space,event_type='DOCUMENT_UPLOAD',occurred_at=document.uploaded_at,source_entity='Document',source_entity_id=str(document.pk),title=f'بارگذاری سند: {document.title}',description=document.document_type,responsible_person=user.get_full_name() or user.username,document=document,provenance='سند بارگذاری‌شده در سامانه',target_url=f'/documents/{document.pk}/download/')
 return document


def open_verified_document(document):
 try:
  handle=document.file.open('rb')
 except (FileNotFoundError,OSError) as exc:
  raise ValidationError('فایل سند در مخزن فیزیکی موجود نیست.') from exc
 digest=hashlib.sha256()
 size=0
 try:
  while True:
   chunk=handle.read(1024*1024)
   if not chunk:break
   size+=len(chunk);digest.update(chunk)
  if size!=document.byte_size or digest.hexdigest()!=document.sha256:
   raise ValidationError('کنترل صحت فایل ناموفق بود؛ دانلود برای جلوگیری از تحویل فایل مخدوش متوقف شد.')
  handle.seek(0)
  return handle
 except Exception:
  handle.close()
  raise


@transaction.atomic
def archive_document(*,document,user,reason,ip_address=None):
 reason=(reason or "").strip()
 if not reason:
  raise ValidationError("علت بایگانی سند الزامی است.")
 if document.archived_at:
  raise ValidationError("این سند قبلاً بایگانی شده است.")
 from django.utils import timezone
 document.archived_at=timezone.now()
 document.save(update_fields=["archived_at"])
 AuditEvent.objects.create(
  actor=user,action="DOCUMENT_ARCHIVE",entity_type=document.entity_type,entity_id=str(document.entity_id),
  reason=reason,before={"document_id":document.pk,"status":"ACTIVE"},
  after={"document_id":document.pk,"status":"ARCHIVED","archived_at":document.archived_at.isoformat()},
  ip_address=ip_address,
 )
 if document.entity_type=="CommercialSpace":
  from domains.operations.models import TimelineEvent
  from domains.properties.models import CommercialSpace
  space=CommercialSpace.objects.filter(code=str(document.entity_id)).first()
  if space:
   TimelineEvent.objects.create(
    space=space,event_type="DOCUMENT_ARCHIVE",occurred_at=document.archived_at,
    source_entity="Document",source_entity_id=str(document.pk),title=f"بایگانی سند: {document.title}",
    description=reason,responsible_person=user.get_full_name() or user.username,document=document,
    provenance="سند بایگانی‌شده در سامانه",target_url=f"/spaces/{space.code}/",
   )
 return document
