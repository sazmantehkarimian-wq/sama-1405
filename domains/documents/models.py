from pathlib import Path
from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db import models
class Document(models.Model):
 title=models.CharField(max_length=255)
 document_type=models.CharField(max_length=80)
 reference=models.CharField(max_length=255,blank=True)
 document_date=models.CharField(max_length=10,blank=True)
 notes=models.TextField(blank=True)
 file=models.FileField(upload_to='documents/%Y/%m/',validators=[FileExtensionValidator(['pdf','docx','xlsx','png','jpg','jpeg'])])
 original_filename=models.CharField(max_length=255)
 sha256=models.CharField(max_length=64)
 content_type=models.CharField(max_length=120)
 byte_size=models.PositiveBigIntegerField()
 entity_type=models.CharField(max_length=80)
 entity_id=models.CharField(max_length=80)
 uploaded_by=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT)
 uploaded_at=models.DateTimeField(auto_now_add=True)
 archived_at=models.DateTimeField(null=True,blank=True)
 @property
 def status_label(self): return 'بایگانی‌شده' if self.archived_at else 'فعال'
