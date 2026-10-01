from django.db import models
class Beneficiary(models.Model):
 class Kind(models.TextChoices):
  NATURAL='NATURAL','شخص حقیقی';LEGAL='LEGAL','شخص حقوقی';TRADE_NAME='TRADE_NAME','نام تجاری';UNSPECIFIED='UNSPECIFIED','نوع نامشخص در منبع'
 name=models.CharField(max_length=255,db_index=True); identity_number=models.CharField(max_length=30,blank=True); kind=models.CharField(max_length=30,choices=Kind.choices,default=Kind.UNSPECIFIED); contact=models.CharField(max_length=255,blank=True); archived_at=models.DateTimeField(null=True)
class BeneficiaryAssignment(models.Model):
 space=models.ForeignKey('properties.CommercialSpace',on_delete=models.PROTECT,related_name='beneficiary_assignments'); beneficiary=models.ForeignKey(Beneficiary,on_delete=models.PROTECT); role=models.CharField(max_length=120); start_date=models.CharField(max_length=10,blank=True); end_date=models.CharField(max_length=10,blank=True); status=models.CharField(max_length=40); source_file=models.ForeignKey('registry.SourceFile',null=True,blank=True,on_delete=models.PROTECT); source_row=models.PositiveIntegerField(null=True,blank=True); created_by=models.ForeignKey('auth.User',null=True,blank=True,on_delete=models.PROTECT); created_at=models.DateTimeField(auto_now_add=True,null=True)
class Contract(models.Model):
 space=models.ForeignKey('properties.CommercialSpace',on_delete=models.PROTECT,related_name='contracts'); beneficiary=models.ForeignKey(Beneficiary,null=True,on_delete=models.PROTECT); number=models.CharField(max_length=120,blank=True,db_index=True); signed_date=models.CharField(max_length=10,blank=True); start_date=models.CharField(max_length=10,blank=True); end_date=models.CharField(max_length=10,blank=True); amount_rial=models.DecimalField(max_digits=24,decimal_places=0,null=True); investment_commitment_rial=models.DecimalField(max_digits=24,decimal_places=0,null=True); status=models.CharField(max_length=80,blank=True); signed_state=models.CharField(max_length=80,blank=True); is_historical=models.BooleanField(default=True); source_file=models.ForeignKey('registry.SourceFile',null=True,blank=True,on_delete=models.PROTECT); source_row=models.PositiveIntegerField(null=True,blank=True); created_by=models.ForeignKey('auth.User',null=True,blank=True,on_delete=models.PROTECT); created_at=models.DateTimeField(auto_now_add=True,null=True)
class ContractAmendment(models.Model):
 contract=models.ForeignKey(Contract,on_delete=models.PROTECT,related_name='amendments'); number=models.CharField(max_length=120); effective_date=models.CharField(max_length=10); description=models.TextField(); amount_change_rial=models.DecimalField(max_digits=24,decimal_places=0,null=True)

class ContractCirculation(models.Model):
 class State(models.TextChoices):
  RECEIVED='RECEIVED','دریافت‌شده';READY='READY','آماده ارسال';SIGNING='SIGNING','در گردش امضا';RETURNED='RETURNED','برگشت برای اصلاح';RESEND='RESEND','ارسال مجدد';READY_APPROVAL='READY_APPROVAL','آماده تأیید نهایی';APPROVED='APPROVED','تأیید نهایی‌شده';CONVERTED='CONVERTED','تبدیل‌شده به قرارداد رسمی';CLOSED_NO_CONTRACT='CLOSED_NO_CONTRACT','مختومه بدون قرارداد'
 identity=models.CharField(max_length=30,unique=True,editable=False,blank=True)
 space=models.ForeignKey('properties.CommercialSpace',on_delete=models.PROTECT,related_name='contract_circulations')
 beneficiary=models.ForeignKey(Beneficiary,on_delete=models.PROTECT,related_name='contract_circulations')
 subject=models.CharField(max_length=255); operational_start_date=models.CharField(max_length=10,default='1405/07/01')
 state=models.CharField(max_length=30,choices=State.choices,default=State.RECEIVED)
 next_action=models.CharField(max_length=255);due_date=models.CharField(max_length=10,blank=True);created_by=models.ForeignKey('auth.User',on_delete=models.PROTECT,related_name='created_contract_circulations');created_at=models.DateTimeField(auto_now_add=True)
 official_contract=models.OneToOneField(Contract,null=True,blank=True,on_delete=models.PROTECT,related_name='source_circulation')
 class Meta:indexes=[models.Index(fields=['state','due_date'])]
 def save(self,*args,**kwargs):
  if not self.identity:
   super().save(*args,**kwargs);self.identity=f'CC-{self.pk:06d}';type(self).objects.filter(pk=self.pk).update(identity=self.identity);return
  super().save(*args,**kwargs)

class ContractCustodyTransfer(models.Model):
 circulation=models.ForeignKey(ContractCirculation,on_delete=models.PROTECT,related_name='transfers')
 sender=models.CharField(max_length=255);receiver=models.CharField(max_length=255);unit=models.CharField(max_length=255)
 delivered_at=models.DateTimeField();purpose=models.CharField(max_length=255);next_action=models.CharField(max_length=255);due_date=models.CharField(max_length=10,blank=True);direction=models.CharField(max_length=20,default='OUT')
 signature_status=models.CharField(max_length=80,blank=True);returned_at=models.DateTimeField(null=True,blank=True);return_note=models.TextField(blank=True);document=models.ForeignKey('documents.Document',null=True,blank=True,on_delete=models.PROTECT);created_by=models.ForeignKey('auth.User',on_delete=models.PROTECT);created_at=models.DateTimeField(auto_now_add=True)
 class Meta:
  constraints=[models.UniqueConstraint(fields=['circulation'],condition=models.Q(returned_at__isnull=True),name='one_open_contract_custody')]
  ordering=['-delivered_at','-id']

class ContractSignatureStep(models.Model):
 class Status(models.TextChoices):PENDING='PENDING','در انتظار ارسال';SENT='SENT','ارسال‌شده برای امضا';SIGNED='SIGNED','امضاشده';RETURNED='RETURNED','برگشت برای اصلاح';WAIVED='WAIVED','صرف‌نظر از مرحله اختیاری'
 circulation=models.ForeignKey(ContractCirculation,on_delete=models.PROTECT,related_name='signature_steps');order=models.PositiveSmallIntegerField();role=models.CharField(max_length=120);person=models.CharField(max_length=255,blank=True);unit=models.CharField(max_length=255);required=models.BooleanField(default=True);sent_at=models.DateTimeField(null=True,blank=True);signed_at=models.DateTimeField(null=True,blank=True);returned_at=models.DateTimeField(null=True,blank=True);status=models.CharField(max_length=20,choices=Status.choices,default=Status.PENDING);note=models.TextField(blank=True);document=models.ForeignKey('documents.Document',null=True,blank=True,on_delete=models.PROTECT);updated_by=models.ForeignKey('auth.User',on_delete=models.PROTECT);updated_at=models.DateTimeField(auto_now=True)
 class Meta:ordering=['order','id'];constraints=[models.UniqueConstraint(fields=['circulation','order'],name='unique_signature_order')]

class ContractFinalApproval(models.Model):
 circulation=models.OneToOneField(ContractCirculation,on_delete=models.PROTECT,related_name='final_approval');approver=models.ForeignKey('auth.User',on_delete=models.PROTECT);approved_at=models.DateTimeField();note=models.TextField(blank=True);created_at=models.DateTimeField(auto_now_add=True)
