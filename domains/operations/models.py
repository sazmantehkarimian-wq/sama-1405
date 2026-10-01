from django.conf import settings
from django.db import models
class Appraiser(models.Model):
 class CollaborationStatus(models.TextChoices):
  ACTIVE='ACTIVE','فعال';INACTIVE='INACTIVE','غیرفعال'
 first_name=models.CharField(max_length=120); last_name=models.CharField(max_length=160)
 national_id=models.CharField(max_length=10,blank=True,db_index=True); license_number=models.CharField(max_length=80,blank=True,db_index=True)
 specialty=models.CharField(max_length=255,blank=True); professional_authority=models.CharField(max_length=255,blank=True)
 mobile=models.CharField(max_length=20,blank=True); phone=models.CharField(max_length=30,blank=True); address=models.TextField(blank=True); email=models.EmailField(blank=True)
 collaboration_status=models.CharField(max_length=20,choices=CollaborationStatus.choices,default=CollaborationStatus.ACTIVE)
 notes=models.TextField(blank=True); archived_at=models.DateTimeField(null=True,blank=True)
 created_by=models.ForeignKey(settings.AUTH_USER_MODEL,null=True,blank=True,on_delete=models.PROTECT,related_name='created_appraisers')
 created_at=models.DateTimeField(auto_now_add=True); updated_at=models.DateTimeField(auto_now=True)
 class Meta:
  ordering=['last_name','first_name','pk']
  constraints=[
   models.UniqueConstraint(fields=['national_id'],condition=~models.Q(national_id=''),name='uniq_nonblank_appraiser_national_id'),
   models.UniqueConstraint(fields=['license_number'],condition=~models.Q(license_number=''),name='uniq_nonblank_appraiser_license'),
  ]
 @property
 def sama_code(self): return f'EXP-{self.pk:06d}' if self.pk else '—'
 @property
 def full_name(self): return f'{self.first_name} {self.last_name}'.strip()
 def __str__(self): return f'{self.sama_code} — {self.full_name}'


class Appraisal(models.Model):
 space=models.ForeignKey('properties.CommercialSpace',on_delete=models.PROTECT,related_name='appraisals')
 appraiser=models.CharField(max_length=255,blank=True)
 appraiser_ref=models.ForeignKey(Appraiser,null=True,blank=True,on_delete=models.PROTECT,related_name='appraisals')
 year=models.CharField(max_length=4,blank=True); sequence=models.CharField(max_length=20,blank=True)
 amount_rial=models.DecimalField(max_digits=24,decimal_places=0,null=True,blank=True)
 reference=models.CharField(max_length=255,blank=True)
 response_number=models.CharField(max_length=120,blank=True); response_date=models.CharField(max_length=10,blank=True)
 appraisal_date=models.CharField(max_length=10,blank=True); status=models.CharField(max_length=80,blank=True)
 is_current=models.BooleanField(default=False); notes=models.TextField(blank=True)
 created_by=models.ForeignKey(settings.AUTH_USER_MODEL,null=True,blank=True,on_delete=models.PROTECT)
 created_at=models.DateTimeField(auto_now_add=True,null=True); updated_at=models.DateTimeField(auto_now=True)
 class Meta:
  ordering=['-appraisal_date','-id']
  constraints=[
   models.UniqueConstraint(fields=['space'],condition=models.Q(is_current=True),name='one_current_appraisal_per_space'),
   models.CheckConstraint(condition=models.Q(amount_rial__isnull=True)|models.Q(amount_rial__gte=0),name='appraisal_amount_nonnegative'),
  ]
 @property
 def sama_code(self): return f'APR-{self.pk:06d}' if self.pk else '—'
 @property
 def appraiser_display(self): return self.appraiser_ref.full_name if self.appraiser_ref_id else self.appraiser
 def __str__(self): return f'{self.sama_code} — فضای {self.space.code}'


class AppraisalNotification(models.Model):
 class Recipient(models.TextChoices):
  EXPERT='EXPERT','کارشناس';REGION='REGION','منطقه';BOTH='BOTH','کارشناس و منطقه';OTHER='OTHER','سایر'
 appraisal=models.ForeignKey(Appraisal,on_delete=models.PROTECT,related_name='notifications')
 number=models.CharField(max_length=120,blank=True); notification_date=models.CharField(max_length=10)
 recipient=models.CharField(max_length=20,choices=Recipient.choices); recipient_detail=models.CharField(max_length=255,blank=True)
 notes=models.TextField(blank=True)
 document=models.ForeignKey('documents.Document',null=True,blank=True,on_delete=models.PROTECT,related_name='appraisal_notifications')
 created_by=models.ForeignKey(settings.AUTH_USER_MODEL,null=True,blank=True,on_delete=models.PROTECT)
 created_at=models.DateTimeField(auto_now_add=True)
 class Meta:
  ordering=['-notification_date','-id']


class AppraisalFee(models.Model):
 appraisal=models.OneToOneField(Appraisal,on_delete=models.PROTECT,related_name='fee'); amount_rial=models.DecimalField(max_digits=24,decimal_places=0); payment_status=models.CharField(max_length=30); payment_date=models.CharField(max_length=10,blank=True); payment_reference=models.CharField(max_length=255,blank=True); follow_up_date=models.CharField(max_length=10,blank=True); notes=models.TextField(blank=True); supporting_document=models.ForeignKey('documents.Document',null=True,blank=True,on_delete=models.PROTECT,related_name='appraisal_fees')
class Auction(models.Model):
 space=models.ForeignKey('properties.CommercialSpace',on_delete=models.PROTECT,related_name='auctions'); year=models.CharField(max_length=4,blank=True); sequence=models.CharField(max_length=20,blank=True); stage=models.CharField(max_length=120,blank=True); result=models.CharField(max_length=120,blank=True); notes=models.TextField(blank=True)
class AuctionRule(models.Model):
 version=models.CharField(max_length=40,unique=True); effective_year=models.PositiveSmallIntegerField(); contract_window_min_days=models.PositiveSmallIntegerField(default=1); contract_window_max_days=models.PositiveSmallIntegerField(default=90); minor_ceiling_rial=models.DecimalField(max_digits=24,decimal_places=0); medium_ceiling_rial=models.DecimalField(max_digits=24,decimal_places=0); appraisal_valid_months=models.PositiveSmallIntegerField(default=6); active=models.BooleanField(default=False); change_reason=models.TextField(); approved_by=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT); created_at=models.DateTimeField(auto_now_add=True)
class AuctionEvaluation(models.Model):
 class Decision(models.TextChoices): CANDIDATE='CANDIDATE','کاندیدا'; NOT_CANDIDATE='NOT_CANDIDATE','غیرکاندیدا'; REVIEW_REQUIRED='REVIEW_REQUIRED','نیازمند بررسی'
 space=models.ForeignKey('properties.CommercialSpace',on_delete=models.PROTECT,related_name='auction_evaluations'); rule=models.ForeignKey(AuctionRule,on_delete=models.PROTECT); decision=models.CharField(max_length=30,choices=Decision.choices); readiness=models.CharField(max_length=30); reason_codes=models.JSONField(); snapshot=models.JSONField(); evaluated_at=models.DateTimeField(auto_now_add=True); evaluated_by=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT)
class AuctionPeriod(models.Model):
 class State(models.TextChoices): DRAFT='DRAFT','پیش‌نویس'; READY='READY','آماده'; OPENED='OPENED','بازگشایی‌شده'; CLOSED='CLOSED','مختومه'; CANCELLED='CANCELLED','لغوشده'
 identity=models.CharField(max_length=80,unique=True); title=models.CharField(max_length=255); planned_date=models.CharField(max_length=10); state=models.CharField(max_length=20,choices=State.choices,default=State.DRAFT); created_by=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT); created_at=models.DateTimeField(auto_now_add=True)
class AuctionLot(models.Model):
 period=models.ForeignKey(AuctionPeriod,on_delete=models.PROTECT,related_name='lots'); space=models.ForeignKey('properties.CommercialSpace',on_delete=models.PROTECT,related_name='auction_lots'); evaluation=models.ForeignKey(AuctionEvaluation,on_delete=models.PROTECT); readiness=models.CharField(max_length=30); result=models.CharField(max_length=120,blank=True); winner_name=models.CharField(max_length=255,blank=True); winning_amount_rial=models.DecimalField(max_digits=24,decimal_places=0,null=True); archived=models.BooleanField(default=False)
 class Meta: constraints=[models.UniqueConstraint(fields=['period','space'],name='one_space_per_auction_period')]
class AuctionParticipant(models.Model):
 period=models.ForeignKey(AuctionPeriod,on_delete=models.PROTECT,related_name='participants'); name=models.CharField(max_length=255); identity_number=models.CharField(max_length=30,blank=True); contact=models.CharField(max_length=120,blank=True)
class AuctionProposal(models.Model):
 lot=models.ForeignKey(AuctionLot,on_delete=models.PROTECT,related_name='proposals'); participant=models.ForeignKey(AuctionParticipant,on_delete=models.PROTECT,related_name='proposals'); received_at=models.DateTimeField(); envelope_a_received=models.BooleanField(default=False); envelope_b_received=models.BooleanField(default=False); envelope_c_received=models.BooleanField(default=False); offered_amount_rial=models.DecimalField(max_digits=24,decimal_places=0,null=True); status=models.CharField(max_length=30); document=models.ForeignKey('documents.Document',null=True,blank=True,on_delete=models.PROTECT)
class CommissionDecision(models.Model):
 class State(models.TextChoices): DRAFT='DRAFT','پیش‌نویس'; APPROVED='APPROVED','تصویب‌شده'; CLOSED='CLOSED','مختومه'; CANCELLED='CANCELLED','لغوشده'
 identity=models.CharField(max_length=120); decision_date=models.CharField(max_length=10); subject=models.CharField(max_length=255); decision=models.TextField(); subsequent_action=models.TextField(blank=True); participants=models.TextField(blank=True); state=models.CharField(max_length=20,choices=State.choices,default=State.DRAFT); document=models.ForeignKey('documents.Document',null=True,blank=True,on_delete=models.PROTECT,related_name='commission_decisions'); spaces=models.ManyToManyField('properties.CommercialSpace',related_name='commission_decisions')
class UtilityRecord(models.Model):
 class Type(models.TextChoices): ELECTRICITY='ELECTRICITY','برق'; WATER='WATER','آب'; GAS='GAS','گاز'; OTHER='OTHER','سایر'
 space=models.ForeignKey('properties.CommercialSpace',on_delete=models.PROTECT,related_name='utilities'); utility_type=models.CharField(max_length=20,choices=Type.choices); account_number=models.CharField(max_length=100); period_start=models.CharField(max_length=10); period_end=models.CharField(max_length=10); consumption=models.DecimalField(max_digits=18,decimal_places=3,null=True); bill_amount_rial=models.DecimalField(max_digits=24,decimal_places=0); organization_share_rial=models.DecimalField(max_digits=24,decimal_places=0); beneficiary_share_rial=models.DecimalField(max_digits=24,decimal_places=0); calculation_basis=models.TextField(); overridden=models.BooleanField(default=False); override_reason=models.TextField(blank=True); payment_status=models.CharField(max_length=30); payment_date=models.CharField(max_length=10,blank=True); supporting_document=models.ForeignKey('documents.Document',null=True,blank=True,on_delete=models.PROTECT,related_name='utility_records')

class UtilityUnit(models.Model):
 class Kind(models.TextChoices):
  REGION='REGION','منطقه';CENTER='CENTER','مرکز خاص';OTHER='OTHER','سایر'
 name=models.CharField(max_length=255)
 kind=models.CharField(max_length=20,choices=Kind.choices)
 region=models.ForeignKey('properties.Region',null=True,blank=True,on_delete=models.PROTECT,related_name='utility_units')
 center=models.ForeignKey('properties.Center',null=True,blank=True,on_delete=models.PROTECT,related_name='utility_units')
 active=models.BooleanField(default=True)
 created_by=models.ForeignKey(settings.AUTH_USER_MODEL,null=True,blank=True,on_delete=models.PROTECT,related_name='created_utility_units')
 created_at=models.DateTimeField(auto_now_add=True)
 class Meta:
  ordering=['name','pk']
  constraints=[
   models.UniqueConstraint(fields=['name','kind'],name='uniq_utility_unit_name_kind'),
   models.CheckConstraint(
    condition=(
     models.Q(kind='REGION',region__isnull=False,center__isnull=True)
     | models.Q(kind='CENTER',center__isnull=False)
     | models.Q(kind='OTHER')
    ),
    name='utility_unit_kind_link_valid',
   ),
  ]
 def __str__(self): return self.name


class UtilityMeasurement(models.Model):
 class Type(models.TextChoices):
  ELECTRICITY='ELECTRICITY','برق';WATER='WATER','آب';GAS='GAS','گاز';OTHER='OTHER','سایر'
 space=models.ForeignKey('properties.CommercialSpace',on_delete=models.PROTECT,related_name='utility_measurements')
 utility_type=models.CharField(max_length=20,choices=Type.choices)
 period_start=models.CharField(max_length=10);period_end=models.CharField(max_length=10)
 consumption=models.DecimalField(max_digits=20,decimal_places=3)
 reading_date=models.CharField(max_length=10)
 meter_number=models.CharField(max_length=120,blank=True)
 measurement_unit=models.CharField(max_length=40,default='kWh')
 source=models.CharField(max_length=120,blank=True)
 is_submeter=models.BooleanField(default=False)
 is_valid=models.BooleanField(default=True)
 notes=models.TextField(blank=True)
 created_by=models.ForeignKey(settings.AUTH_USER_MODEL,null=True,blank=True,on_delete=models.PROTECT)
 created_at=models.DateTimeField(auto_now_add=True)
 class Meta:
  ordering=['-reading_date','-id']
  constraints=[
   models.CheckConstraint(condition=models.Q(consumption__gte=0),name='utility_measurement_nonnegative'),
  ]


class UtilityParameterRule(models.Model):
 key=models.CharField(max_length=120,db_index=True)
 label=models.CharField(max_length=255)
 value_decimal=models.DecimalField(max_digits=20,decimal_places=6,null=True,blank=True)
 value_text=models.CharField(max_length=255,blank=True)
 unit=models.CharField(max_length=40,blank=True)
 effective_from=models.CharField(max_length=10)
 effective_to=models.CharField(max_length=10,blank=True)
 active=models.BooleanField(default=True)
 notes=models.TextField(blank=True)
 created_by=models.ForeignKey(settings.AUTH_USER_MODEL,null=True,blank=True,on_delete=models.PROTECT)
 created_at=models.DateTimeField(auto_now_add=True)
 class Meta:
  ordering=['key','-effective_from','-id']
  constraints=[
   models.UniqueConstraint(fields=['key','effective_from'],name='uniq_utility_rule_key_effective'),
  ]


class ElectricityConsumptionCategory(models.Model):
 name=models.CharField(max_length=255,unique=True)
 eui=models.DecimalField(max_digits=16,decimal_places=6,null=True,blank=True)
 effective_from=models.CharField(max_length=10,blank=True)
 active=models.BooleanField(default=True)
 notes=models.TextField(blank=True)
 created_by=models.ForeignKey(settings.AUTH_USER_MODEL,null=True,blank=True,on_delete=models.PROTECT)
 created_at=models.DateTimeField(auto_now_add=True)
 class Meta: ordering=['name']
 def __str__(self): return self.name


class ElectricityBill(models.Model):
 class Status(models.TextChoices):
  DRAFT='DRAFT','پیش‌نویس';CALCULATED='CALCULATED','محاسبه‌شده';REVIEW_REQUIRED='REVIEW_REQUIRED','نیازمند بررسی';FINAL='FINAL','نهایی';REOPENED='REOPENED','بازگشایی‌شده'
 unit=models.ForeignKey(UtilityUnit,on_delete=models.PROTECT,related_name='electricity_bills')
 period_start=models.CharField(max_length=10);period_end=models.CharField(max_length=10)
 bill_date=models.CharField(max_length=10,blank=True)
 amount_rial=models.DecimalField(max_digits=24,decimal_places=0)
 beneficiary_share_percent=models.DecimalField(max_digits=7,decimal_places=4)
 organization_share_percent=models.DecimalField(max_digits=7,decimal_places=4)
 status=models.CharField(max_length=30,choices=Status.choices,default=Status.DRAFT)
 notes=models.TextField(blank=True)
 supporting_document=models.ForeignKey('documents.Document',null=True,blank=True,on_delete=models.PROTECT,related_name='electricity_bills')
 created_by=models.ForeignKey(settings.AUTH_USER_MODEL,null=True,blank=True,on_delete=models.PROTECT)
 created_at=models.DateTimeField(auto_now_add=True);updated_at=models.DateTimeField(auto_now=True)
 finalized_at=models.DateTimeField(null=True,blank=True);finalized_by=models.ForeignKey(settings.AUTH_USER_MODEL,null=True,blank=True,on_delete=models.PROTECT,related_name='finalized_electricity_bills')
 reopen_reason=models.TextField(blank=True)
 class Meta:
  ordering=['-period_end','-id']
  constraints=[
   models.UniqueConstraint(fields=['unit','period_start','period_end'],name='uniq_electricity_bill_unit_period'),
   models.CheckConstraint(condition=models.Q(amount_rial__gte=0),name='electricity_bill_amount_nonnegative'),
   models.CheckConstraint(condition=models.Q(beneficiary_share_percent__gte=0)&models.Q(beneficiary_share_percent__lte=100),name='electricity_beneficiary_share_range'),
   models.CheckConstraint(condition=models.Q(organization_share_percent__gte=0)&models.Q(organization_share_percent__lte=100),name='electricity_org_share_range'),
  ]
 @property
 def sama_code(self): return f'ELB-{self.pk:06d}' if self.pk else '—'
 @property
 def organization_amount_rial(self):
  from decimal import Decimal, ROUND_HALF_UP
  return (self.amount_rial*self.organization_share_percent/Decimal('100')).quantize(Decimal('1'),rounding=ROUND_HALF_UP)
 def __str__(self): return f'{self.sama_code} — {self.unit.name}'


class ElectricityAllocation(models.Model):
 class Source(models.TextChoices):
  SUBMETER='SUBMETER','زیرکنتور';MEASUREMENT='MEASUREMENT','اندازه‌گیری واقعی';EQUIPMENT='EQUIPMENT','داده تجهیزات';APPROVED_MODEL='APPROVED_MODEL','مدل مصوب';MANUAL_OVERRIDE='MANUAL_OVERRIDE','Override دستی'
 class Confidence(models.TextChoices):
  REAL_MEASUREMENT='REAL_MEASUREMENT','اندازه‌گیری واقعی';VALID_EQUIPMENT='VALID_EQUIPMENT','داده تجهیزات معتبر';APPROVED_MODEL='APPROVED_MODEL','محاسبه مدل مصوب';INCOMPLETE='INCOMPLETE','نیازمند تکمیل';REVIEW='REVIEW','نیازمند بررسی'
 bill=models.ForeignKey(ElectricityBill,on_delete=models.PROTECT,related_name='allocations')
 space=models.ForeignKey('properties.CommercialSpace',on_delete=models.PROTECT,related_name='electricity_allocations')
 eligible=models.BooleanField(default=True)
 category=models.ForeignKey(ElectricityConsumptionCategory,null=True,blank=True,on_delete=models.PROTECT,related_name='allocations')
 effective_area=models.DecimalField(max_digits=16,decimal_places=2,null=True,blank=True)
 eui=models.DecimalField(max_digits=16,decimal_places=6,null=True,blank=True)
 operational_factor=models.DecimalField(max_digits=12,decimal_places=6,null=True,blank=True)
 special_consumption=models.DecimalField(max_digits=20,decimal_places=3,null=True,blank=True)
 measurement=models.ForeignKey(UtilityMeasurement,null=True,blank=True,on_delete=models.PROTECT,related_name='electricity_allocations')
 calculated_share_percent=models.DecimalField(max_digits=7,decimal_places=4,null=True,blank=True)
 manual_override_percent=models.DecimalField(max_digits=7,decimal_places=4,null=True,blank=True)
 final_share_percent=models.DecimalField(max_digits=7,decimal_places=4)
 calculation_source=models.CharField(max_length=30,choices=Source.choices)
 confidence_level=models.CharField(max_length=30,choices=Confidence.choices)
 override_reason=models.TextField(blank=True)
 notes=models.TextField(blank=True)
 payable_amount_rial=models.DecimalField(max_digits=24,decimal_places=0,null=True,blank=True)
 created_by=models.ForeignKey(settings.AUTH_USER_MODEL,null=True,blank=True,on_delete=models.PROTECT)
 created_at=models.DateTimeField(auto_now_add=True);updated_at=models.DateTimeField(auto_now=True)
 class Meta:
  ordering=['space__code','pk']
  constraints=[
   models.UniqueConstraint(fields=['bill','space'],name='uniq_electricity_allocation_bill_space'),
   models.CheckConstraint(condition=models.Q(final_share_percent__gte=0)&models.Q(final_share_percent__lte=100),name='electricity_final_share_range'),
   models.CheckConstraint(condition=models.Q(calculated_share_percent__isnull=True)|(models.Q(calculated_share_percent__gte=0)&models.Q(calculated_share_percent__lte=100)),name='electricity_calc_share_range'),
   models.CheckConstraint(condition=models.Q(manual_override_percent__isnull=True)|(models.Q(manual_override_percent__gte=0)&models.Q(manual_override_percent__lte=100)),name='electricity_override_share_range'),
  ]
 @property
 def has_override(self): return self.manual_override_percent is not None


class ElectricityCalculationSnapshot(models.Model):
 bill=models.ForeignKey(ElectricityBill,on_delete=models.PROTECT,related_name='snapshots')
 version=models.PositiveIntegerField()
 payload=models.JSONField()
 reason=models.TextField(blank=True)
 created_by=models.ForeignKey(settings.AUTH_USER_MODEL,null=True,blank=True,on_delete=models.PROTECT)
 created_at=models.DateTimeField(auto_now_add=True)
 class Meta:
  ordering=['-version','-id']
  constraints=[models.UniqueConstraint(fields=['bill','version'],name='uniq_electricity_snapshot_version')]


class FileMovement(models.Model):
 space=models.ForeignKey('properties.CommercialSpace',on_delete=models.PROTECT,related_name='file_movements'); location=models.CharField(max_length=255); holder=models.CharField(max_length=255); delivered_by=models.CharField(max_length=255); received_by=models.CharField(max_length=255); handover_at=models.DateTimeField(); returned_at=models.DateTimeField(null=True); signature_state=models.CharField(max_length=50); direction=models.CharField(max_length=20); next_action=models.CharField(max_length=255,blank=True); due_date=models.CharField(max_length=10,blank=True); notes=models.TextField(blank=True); created_by=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT)
class TimelineEvent(models.Model):
 space=models.ForeignKey('properties.CommercialSpace',on_delete=models.PROTECT,related_name='timeline'); event_type=models.CharField(max_length=80); jalali_date=models.CharField(max_length=10,blank=True,db_index=True); occurred_at=models.DateTimeField(null=True); source_entity=models.CharField(max_length=80); source_entity_id=models.CharField(max_length=80); title=models.CharField(max_length=255); description=models.TextField(blank=True); previous_state=models.CharField(max_length=120,blank=True); new_state=models.CharField(max_length=120,blank=True); responsible_person=models.CharField(max_length=255,blank=True); document=models.ForeignKey('documents.Document',null=True,on_delete=models.PROTECT); provenance=models.TextField(); target_url=models.CharField(max_length=500,blank=True)
 class Meta: ordering=['-jalali_date','-occurred_at','-id']
class Alert(models.Model):
 class Priority(models.TextChoices):LOW='LOW','کم';MEDIUM='MEDIUM','متوسط';HIGH='HIGH','زیاد';CRITICAL='CRITICAL','بحرانی'
 space=models.ForeignKey('properties.CommercialSpace',on_delete=models.PROTECT,related_name='alerts'); subject=models.CharField(max_length=255); reason=models.TextField(); effective_date=models.CharField(max_length=10,blank=True); due_date=models.CharField(max_length=10,blank=True); priority=models.CharField(max_length=20,choices=Priority.choices,default=Priority.MEDIUM); status=models.CharField(max_length=30); assigned_to=models.ForeignKey('auth.User',null=True,blank=True,on_delete=models.PROTECT,related_name='assigned_alerts'); acknowledged_at=models.DateTimeField(null=True,blank=True); target_url=models.CharField(max_length=500)

class DecisionOrder(models.Model):
 space=models.ForeignKey('properties.CommercialSpace',on_delete=models.PROTECT,related_name='decisions'); decision_type=models.CharField(max_length=120); decision_date=models.CharField(max_length=10,blank=True); letter_number=models.CharField(max_length=120,blank=True); session_reference=models.CharField(max_length=255,blank=True); text=models.TextField(); review_status=models.CharField(max_length=80,blank=True)

class UtilityObligation(models.Model):
 space=models.ForeignKey('properties.CommercialSpace',on_delete=models.PROTECT,related_name='utility_obligations'); utility_type=models.CharField(max_length=120); calculation_type=models.CharField(max_length=120,blank=True); amount_rial=models.DecimalField(max_digits=24,decimal_places=0,null=True); percentage=models.DecimalField(max_digits=8,decimal_places=3,null=True); standard_description=models.TextField(blank=True); notes=models.TextField(blank=True)

class SourceDocumentReference(models.Model):
 space=models.ForeignKey('properties.CommercialSpace',on_delete=models.PROTECT,related_name='source_documents'); document_type=models.CharField(max_length=120); reference=models.CharField(max_length=255,blank=True); status=models.CharField(max_length=80,blank=True); source_path=models.TextField(blank=True); notes=models.TextField(blank=True)

class WorkflowInstance(models.Model):
 class State(models.TextChoices): OPEN='OPEN','باز'; DONE='DONE','تکمیل‌شده'; CANCELLED='CANCELLED','لغوشده'
 space=models.ForeignKey('properties.CommercialSpace',on_delete=models.PROTECT,related_name='workflows'); process_type=models.CharField(max_length=80); title=models.CharField(max_length=255); state=models.CharField(max_length=20,choices=State.choices,default=State.OPEN); next_action=models.CharField(max_length=255); due_date=models.CharField(max_length=10,blank=True); created_by=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT); created_at=models.DateTimeField(auto_now_add=True); closed_at=models.DateTimeField(null=True)

class OperationalHistory(models.Model):
 entity_type=models.CharField(max_length=80,db_index=True); entity_id=models.CharField(max_length=80,db_index=True); action=models.CharField(max_length=80); previous_state=models.JSONField(null=True); new_state=models.JSONField(null=True); reason=models.TextField(blank=True); responsible=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT); occurred_at=models.DateTimeField(auto_now_add=True)
 class Meta: ordering=['-occurred_at','-id']
