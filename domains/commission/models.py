from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class ImmutableCodeModel(models.Model):
    internal_code = models.CharField(max_length=32, unique=True, editable=False, blank=True)
    code_prefix = ''

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if self.pk:
            original = type(self).objects.filter(pk=self.pk).values_list('internal_code', flat=True).first()
            if original and self.internal_code != original:
                raise ValidationError({'internal_code': 'شناسه داخلی سیستمی قابل تغییر نیست.'})
        super().save(*args, **kwargs)
        if not self.internal_code:
            code = f'{self.code_prefix}{self.pk:06d}'
            type(self).objects.filter(pk=self.pk, internal_code='').update(internal_code=code)
            self.internal_code = code


class CommissionMember(models.Model):
    class Role(models.TextChoices):
        CHAIR = 'CHAIR', 'رئیس'
        SECRETARY = 'SECRETARY', 'دبیر'
        MEMBER = 'MEMBER', 'عضو'
        OBSERVER = 'OBSERVER', 'ناظر / مدعو'

    full_name = models.CharField(max_length=255)
    position = models.CharField(max_length=255)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.MEMBER)
    is_active = models.BooleanField(default=True)
    signature_order = models.PositiveSmallIntegerField(null=True, blank=True)
    membership_start = models.CharField(max_length=10, blank=True)
    membership_end = models.CharField(max_length=10, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['signature_order', 'full_name']

    def __str__(self):
        return self.full_name


class CommissionSession(ImmutableCodeModel):
    class State(models.TextChoices):
        DRAFT = 'DRAFT', 'پیش‌نویس'
        PLANNED = 'PLANNED', 'برنامه‌ریزی‌شده'
        HELD = 'HELD', 'برگزارشده'
        FINALIZED = 'FINALIZED', 'نهایی‌شده'
        CANCELLED = 'CANCELLED', 'لغوشده'

    code_prefix = 'COM-SES-'
    session_number = models.CharField(max_length=120, blank=True)
    session_date = models.CharField(max_length=10, db_index=True)
    session_time = models.CharField(max_length=5, blank=True)
    location = models.CharField(max_length=255, blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    state = models.CharField(max_length=20, choices=State.choices, default=State.DRAFT, db_index=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='commission_sessions_created')
    created_at = models.DateTimeField(auto_now_add=True)
    finalized_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-session_date', '-id']

    def __str__(self):
        return f'{self.internal_code} — {self.title}'


class CommissionSessionMember(models.Model):
    class Attendance(models.TextChoices):
        PRESENT = 'PRESENT', 'حاضر'
        ABSENT = 'ABSENT', 'غایب'
        EXCUSED = 'EXCUSED', 'غایب موجه'

    session = models.ForeignKey(CommissionSession, on_delete=models.PROTECT, related_name='session_members')
    member = models.ForeignKey(CommissionMember, null=True, blank=True, on_delete=models.PROTECT, related_name='session_snapshots')
    full_name = models.CharField(max_length=255)
    position = models.CharField(max_length=255)
    role = models.CharField(max_length=80)
    attendance = models.CharField(max_length=20, choices=Attendance.choices, default=Attendance.PRESENT)
    signature_order = models.PositiveSmallIntegerField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['signature_order', 'id']
        constraints = [models.UniqueConstraint(fields=['session', 'member'], condition=models.Q(member__isnull=False), name='unique_reference_member_per_commission_session')]


class CommissionCase(ImmutableCodeModel):
    class ReviewState(models.TextChoices):
        DRAFT = 'DRAFT', 'پیش‌نویس'
        ON_AGENDA = 'ON_AGENDA', 'در دستور جلسه'
        REVIEWED = 'REVIEWED', 'بررسی‌شده'
        DEFERRED = 'DEFERRED', 'موکول‌شده'
        CLOSED = 'CLOSED', 'مختومه'

    class ExecutionState(models.TextChoices):
        NOT_REQUIRED = 'NOT_REQUIRED', 'نیازمند اجرا نیست'
        PENDING = 'PENDING', 'در انتظار اجرا'
        IN_PROGRESS = 'IN_PROGRESS', 'در حال اجرا'
        DONE = 'DONE', 'انجام‌شده'
        OVERDUE = 'OVERDUE', 'سررسید گذشته'

    code_prefix = 'COM-CASE-'
    session = models.ForeignKey(CommissionSession, on_delete=models.PROTECT, related_name='cases')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    referral_reason = models.TextField()
    case_type = models.CharField(max_length=120)
    referral_source = models.CharField(max_length=255, blank=True)
    review_state = models.CharField(max_length=20, choices=ReviewState.choices, default=ReviewState.ON_AGENDA, db_index=True)
    result_summary = models.TextField(blank=True)
    follow_up_owner = models.CharField(max_length=255, blank=True)
    execution_state = models.CharField(max_length=20, choices=ExecutionState.choices, default=ExecutionState.NOT_REQUIRED, db_index=True)
    follow_up_deadline = models.CharField(max_length=10, blank=True, db_index=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='commission_cases_created')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['session_id', 'id']


class CommissionRelatedEntity(models.Model):
    case = models.ForeignKey(CommissionCase, on_delete=models.PROTECT, related_name='related_entities')
    space = models.ForeignKey('properties.CommercialSpace', null=True, blank=True, on_delete=models.PROTECT, related_name='commission_cases')
    contract = models.ForeignKey('contracts.Contract', null=True, blank=True, on_delete=models.PROTECT, related_name='commission_cases')
    beneficiary = models.ForeignKey('contracts.Beneficiary', null=True, blank=True, on_delete=models.PROTECT, related_name='commission_cases')
    auction_period = models.ForeignKey('operations.AuctionPeriod', null=True, blank=True, on_delete=models.PROTECT, related_name='commission_cases')
    mother_property = models.ForeignKey('properties.MotherProperty', null=True, blank=True, on_delete=models.PROTECT, related_name='commission_cases')
    notes = models.CharField(max_length=255, blank=True)

    class Meta:
        constraints = [models.CheckConstraint(
            condition=(
                models.Q(space__isnull=False, contract__isnull=True, beneficiary__isnull=True, auction_period__isnull=True, mother_property__isnull=True)
                | models.Q(space__isnull=True, contract__isnull=False, beneficiary__isnull=True, auction_period__isnull=True, mother_property__isnull=True)
                | models.Q(space__isnull=True, contract__isnull=True, beneficiary__isnull=False, auction_period__isnull=True, mother_property__isnull=True)
                | models.Q(space__isnull=True, contract__isnull=True, beneficiary__isnull=True, auction_period__isnull=False, mother_property__isnull=True)
                | models.Q(space__isnull=True, contract__isnull=True, beneficiary__isnull=True, auction_period__isnull=True, mother_property__isnull=False)
            ),
            name='commission_related_entity_exactly_one_target',
        )]


class CommissionDecision(ImmutableCodeModel):
    class ExecutionState(models.TextChoices):
        PENDING = 'PENDING', 'در انتظار اجرا'
        IN_PROGRESS = 'IN_PROGRESS', 'در حال اجرا'
        DONE = 'DONE', 'انجام‌شده'
        CANCELLED = 'CANCELLED', 'لغوشده'

    code_prefix = 'COM-DEC-'
    case = models.ForeignKey(CommissionCase, on_delete=models.PROTECT, related_name='decisions')
    decision_date = models.CharField(max_length=10, db_index=True)
    decision_type = models.CharField(max_length=120)
    formal_text = models.TextField()
    result = models.CharField(max_length=255, blank=True)
    execution_owner = models.CharField(max_length=255, blank=True)
    execution_deadline = models.CharField(max_length=10, blank=True, db_index=True)
    execution_state = models.CharField(max_length=20, choices=ExecutionState.choices, default=ExecutionState.PENDING, db_index=True)
    notes = models.TextField(blank=True)
    document = models.ForeignKey('documents.Document', null=True, blank=True, on_delete=models.PROTECT, related_name='commission_formal_decisions')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='commission_decisions_created')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-decision_date', '-id']


class CommissionFollowUp(models.Model):
    class State(models.TextChoices):
        OPEN = 'OPEN', 'باز'
        IN_PROGRESS = 'IN_PROGRESS', 'در حال پیگیری'
        DONE = 'DONE', 'انجام‌شده'
        CANCELLED = 'CANCELLED', 'لغوشده'

    decision = models.ForeignKey(CommissionDecision, on_delete=models.PROTECT, related_name='follow_ups')
    action = models.TextField()
    owner = models.CharField(max_length=255)
    due_date = models.CharField(max_length=10, blank=True, db_index=True)
    state = models.CharField(max_length=20, choices=State.choices, default=State.OPEN, db_index=True)
    outcome = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='commission_followups_created')
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['state', 'due_date', 'id']


class CommissionSessionDocument(models.Model):
    session = models.ForeignKey(CommissionSession, on_delete=models.PROTECT, related_name='session_documents')
    document = models.ForeignKey('documents.Document', on_delete=models.PROTECT, related_name='commission_sessions')
    document_role = models.CharField(max_length=120, default='صورتجلسه')
    notes = models.CharField(max_length=255, blank=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['session', 'document'], name='unique_document_per_commission_session')]
