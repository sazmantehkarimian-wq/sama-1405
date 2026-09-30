import hashlib
from pathlib import Path
from django.core.exceptions import ValidationError
from django.db import transaction
from domains.documents.models import Document
from domains.identity.models import AuditEvent

ALLOWED={'.pdf':'application/pdf','.docx':'application/vnd.openxmlformats-officedocument.wordprocessingml.document','.xlsx':'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet','.png':'image/png','.jpg':'image/jpeg','.jpeg':'image/jpeg'}
MAX_BYTES=10*1024*1024

@transaction.atomic
def store_document(*,uploaded,title,document_type,entity_type,entity_id,user,ip_address=None):
 suffix=Path(uploaded.name).suffix.lower()
 if suffix not in ALLOWED:raise ValidationError('نوع فایل مجاز نیست.')
 if uploaded.size>MAX_BYTES:raise ValidationError('حجم فایل بیش از حد مجاز است.')
 digest=hashlib.sha256()
 for chunk in uploaded.chunks():digest.update(chunk)
 uploaded.seek(0)
 document=Document.objects.create(title=title,document_type=document_type,file=uploaded,original_filename=Path(uploaded.name).name,sha256=digest.hexdigest(),content_type=ALLOWED[suffix],byte_size=uploaded.size,entity_type=entity_type,entity_id=str(entity_id),uploaded_by=user)
 AuditEvent.objects.create(actor=user,action='DOCUMENT_UPLOAD',entity_type=entity_type,entity_id=str(entity_id),after={'document_id':document.pk,'sha256':document.sha256},ip_address=ip_address)
 return document
