from django.conf import settings
from django.db import models


class AuctionPeriodProfile(models.Model):
    period = models.OneToOneField('operations.AuctionPeriod', on_delete=models.PROTECT, related_name='flow_profile')
    permit_reference = models.CharField(max_length=255, blank=True)
    ad_day_name = models.CharField(max_length=40, blank=True)
    ad_date = models.CharField(max_length=10, blank=True)
    newspaper = models.CharField(max_length=120, blank=True, default='همشهری')
    invitation_number = models.CharField(max_length=120, blank=True)
    opening_session_date = models.CharField(max_length=10, blank=True)
    opening_session_time = models.CharField(max_length=5, blank=True)
    opening_session_location = models.CharField(max_length=255, blank=True)
    duration_years = models.PositiveSmallIntegerField(default=1)
    template_version = models.CharField(max_length=80, default='reference-1405-07-12-v1')
    notes = models.TextField(blank=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.PROTECT)
    updated_at = models.DateTimeField(auto_now=True)


class AuctionLotProfile(models.Model):
    class Family(models.TextChoices):
        COMMERCIAL = 'COMMERCIAL', 'تجاری'
        CAFE = 'CAFE', 'کافه'
        SPORT = 'SPORT', 'ورزشی'

    class ResultState(models.TextChoices):
        OPEN = 'OPEN', 'در جریان'
        AWARDED = 'AWARDED', 'برنده تعیین شده'
        CONTRACTING = 'CONTRACTING', 'در فرایند قرارداد'
        CONTRACTED = 'CONTRACTED', 'قرارداد نهایی شده'
        NO_WINNER = 'NO_WINNER', 'بدون برنده'
        CANCELLED = 'CANCELLED', 'لغو شده'

    lot = models.OneToOneField('operations.AuctionLot', on_delete=models.PROTECT, related_name='flow_profile')
    template_family = models.CharField(max_length=20, choices=Family.choices, default=Family.COMMERCIAL)
    base_monthly_rent_rial = models.DecimalField(max_digits=24, decimal_places=0, null=True, blank=True)
    guarantee_amount_rial = models.DecimalField(max_digits=24, decimal_places=0, null=True, blank=True)
    investment_amount_rial = models.DecimalField(max_digits=24, decimal_places=0, null=True, blank=True)
    proposed_job = models.CharField(max_length=255, blank=True)
    winner_proposal = models.ForeignKey('operations.AuctionProposal', null=True, blank=True, on_delete=models.PROTECT, related_name='won_lot_profiles')
    runner_up_proposal = models.ForeignKey('operations.AuctionProposal', null=True, blank=True, on_delete=models.PROTECT, related_name='runner_up_lot_profiles')
    decision_reference = models.CharField(max_length=255, blank=True)
    decision_date = models.CharField(max_length=10, blank=True)
    result_state = models.CharField(max_length=30, choices=ResultState.choices, default=ResultState.OPEN)
    beneficiary = models.ForeignKey('contracts.Beneficiary', null=True, blank=True, on_delete=models.PROTECT, related_name='auction_awards')
    contract_circulation = models.OneToOneField('contracts.ContractCirculation', null=True, blank=True, on_delete=models.PROTECT, related_name='auction_award')
    official_contract = models.OneToOneField('contracts.Contract', null=True, blank=True, on_delete=models.PROTECT, related_name='auction_award')
    snapshot = models.JSONField(default=dict, blank=True)
    awarded_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.PROTECT, related_name='auction_awards_made')
    awarded_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(condition=models.Q(base_monthly_rent_rial__isnull=True) | models.Q(base_monthly_rent_rial__gte=0), name='auctionflow_base_rent_nonnegative'),
            models.CheckConstraint(condition=models.Q(guarantee_amount_rial__isnull=True) | models.Q(guarantee_amount_rial__gte=0), name='auctionflow_guarantee_nonnegative'),
            models.CheckConstraint(condition=models.Q(investment_amount_rial__isnull=True) | models.Q(investment_amount_rial__gte=0), name='auctionflow_investment_nonnegative'),
        ]


class AuctionDocumentInstance(models.Model):
    class DocumentType(models.TextChoices):
        CONDITIONS = 'CONDITIONS', 'شرایط عمومی و اختصاصی'
        PRICE_FORM = 'PRICE_FORM', 'فرم پیشنهاد قیمت / روکش پاکات'
        OPENING_MINUTES = 'OPENING_MINUTES', 'صورتجلسه بازگشایی پاکات'
        EXPERT_NOTICE = 'EXPERT_NOTICE', 'ابلاغ کارشناس رسمی'
        SAMPLE_CONTRACT = 'SAMPLE_CONTRACT', 'نمونه قرارداد'
        ENVELOPE_A = 'ENVELOPE_A', 'پاکت الف'
        ENVELOPE_B = 'ENVELOPE_B', 'پاکت ب'
        ENVELOPE_C = 'ENVELOPE_C', 'پاکت ج'

    class Status(models.TextChoices):
        UAT_DRAFT = 'UAT_DRAFT', 'پیش‌نویس کنترل‌شده UAT'
        APPROVED = 'APPROVED', 'تأییدشده'
        INVALIDATED = 'INVALIDATED', 'باطل‌شده'

    period = models.ForeignKey('operations.AuctionPeriod', on_delete=models.PROTECT, related_name='generated_documents')
    lot = models.ForeignKey('operations.AuctionLot', null=True, blank=True, on_delete=models.PROTECT, related_name='generated_documents')
    document_type = models.CharField(max_length=30, choices=DocumentType.choices)
    template_family = models.CharField(max_length=20, choices=AuctionLotProfile.Family.choices, blank=True)
    template_version = models.CharField(max_length=80)
    source_sha256 = models.CharField(max_length=64)
    snapshot = models.JSONField()
    snapshot_sha256 = models.CharField(max_length=64)
    document = models.ForeignKey('documents.Document', on_delete=models.PROTECT, related_name='auction_generated_instances')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.UAT_DRAFT)
    generated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    generated_at = models.DateTimeField(auto_now_add=True)
    invalidated_at = models.DateTimeField(null=True, blank=True)
    invalidation_reason = models.TextField(blank=True)

    class Meta:
        ordering = ['-generated_at', '-pk']
        indexes = [models.Index(fields=['period', 'lot', 'document_type', 'status'])]
