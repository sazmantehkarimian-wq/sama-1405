from django.conf import settings
from django.db import models
class UserProfile(models.Model):
 user=models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='profile'); must_change_password=models.BooleanField(default=True); display_name=models.CharField(max_length=255); operational_access=models.BooleanField(default=True)
class AuditEvent(models.Model):
 actor=models.ForeignKey(settings.AUTH_USER_MODEL,null=True,on_delete=models.PROTECT); action=models.CharField(max_length=80); entity_type=models.CharField(max_length=80); entity_id=models.CharField(max_length=80); reason=models.TextField(blank=True); before=models.JSONField(null=True); after=models.JSONField(null=True); created_at=models.DateTimeField(auto_now_add=True); ip_address=models.GenericIPAddressField(null=True)
class HardDeleteRequest(models.Model):
 object_type=models.CharField(max_length=80); object_id=models.CharField(max_length=80); reason=models.TextField(); requested_by=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT); confirmed_at=models.DateTimeField(null=True); audit_event=models.OneToOneField(AuditEvent,null=True,on_delete=models.PROTECT)
class SavedFilter(models.Model):
 owner=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE); name=models.CharField(max_length=120); domain=models.CharField(max_length=80); definition=models.JSONField(); is_shared=models.BooleanField(default=False)
class SavedReport(models.Model):
 owner=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE); name=models.CharField(max_length=120); domain=models.CharField(max_length=80); fields=models.JSONField(); filters=models.JSONField(); sorting=models.JSONField(); grouping=models.JSONField(); blank_columns=models.JSONField(default=list); blank_rows=models.PositiveSmallIntegerField(default=0); layout=models.JSONField(default=list); orientation=models.CharField(max_length=20,default='landscape')
class ArchivedReportSnapshot(models.Model):
 report=models.ForeignKey(SavedReport,on_delete=models.PROTECT); generated_by=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT); generated_at=models.DateTimeField(auto_now_add=True); query_context=models.JSONField(); row_count=models.PositiveIntegerField(); sha256=models.CharField(max_length=64); file=models.FileField(upload_to='report-snapshots/%Y/%m/')
