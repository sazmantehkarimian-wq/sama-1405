from decimal import Decimal
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q


class Beneficiary(models.Model):
    class Kind(models.TextChoices):
        NATURAL = "NATURAL", "شخص حقیقی"
        LEGAL = "LEGAL", "شخص حقوقی"

    name = models.CharField(max_length=255, db_index=True)
    identity_number = models.CharField(max_length=11, blank=True, db_index=True)
    kind = models.CharField(max_length=20, choices=Kind.choices)

    first_name = models.CharField(max_length=120, blank=True)
    last_name = models.CharField(max_length=160, blank=True)
    father_name = models.CharField(max_length=120, blank=True)
    birth_certificate_number = models.CharField(max_length=30, blank=True)
    birth_date = models.CharField(max_length=10, blank=True)

    legal_name = models.CharField(max_length=255, blank=True)
    registration_number = models.CharField(max_length=60, blank=True)
    legal_entity_type = models.CharField(max_length=80, blank=True)
    economic_code = models.CharField(max_length=30, blank=True)
    representative_name = models.CharField(max_length=255, blank=True)

    mobile = models.CharField(max_length=20, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    contact = models.CharField(max_length=255, blank=True)
    address = models.TextField(blank=True)
    postal_code = models.CharField(max_length=20, blank=True)

    archived_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey("auth.User", null=True, blank=True, on_delete=models.PROTECT, related_name="created_beneficiaries")
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name", "pk"]
        constraints = [
            models.UniqueConstraint(
                fields=["identity_number"],
                condition=~Q(identity_number=""),
                name="uniq_nonblank_beneficiary_identity",
            ),
        ]

    @property
    def sama_code(self):
        return f"B-{self.pk:06d}" if self.pk else "—"

    @property
    def completeness_status(self):
        if not self.identity_number:
            return "نیازمند تکمیل هویت"
        if self.kind == self.Kind.NATURAL and not self.mobile:
            return "نیازمند تکمیل"
        return "کامل"

    def __str__(self):
        return f"{self.sama_code} — {self.name}"


class BeneficiaryAssignment(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "جاری"
        ENDED = "ENDED", "خاتمه‌یافته"

    space = models.ForeignKey("properties.CommercialSpace", on_delete=models.PROTECT, related_name="beneficiary_assignments")
    beneficiary = models.ForeignKey(Beneficiary, on_delete=models.PROTECT, related_name="space_assignments")
    role = models.CharField(max_length=120)
    start_date = models.CharField(max_length=10, blank=True)
    end_date = models.CharField(max_length=10, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    basis = models.CharField(max_length=120, blank=True)
    termination_reason = models.TextField(blank=True)
    created_by = models.ForeignKey("auth.User", null=True, blank=True, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        ordering = ["-start_date", "-id"]


class Contract(models.Model):
    space = models.ForeignKey("properties.CommercialSpace", on_delete=models.PROTECT, related_name="contracts")
    beneficiary = models.ForeignKey(Beneficiary, on_delete=models.PROTECT, related_name="contracts")
    number = models.CharField(max_length=120, db_index=True)
    subject = models.CharField(max_length=255, blank=True)
    signed_date = models.CharField(max_length=10, blank=True)
    start_date = models.CharField(max_length=10)
    end_date = models.CharField(max_length=10)
    amount_rial = models.DecimalField(max_digits=24, decimal_places=0, null=True, blank=True, validators=[MinValueValidator(Decimal("0"))])
    investment_commitment_rial = models.DecimalField(max_digits=24, decimal_places=0, null=True, blank=True, validators=[MinValueValidator(Decimal("0"))])
    status = models.CharField(max_length=80, blank=True, help_text="وضعیت حقوقی قرارداد")
    signed_state = models.CharField(max_length=80, blank=True)
    notes = models.TextField(blank=True)
    is_historical = models.BooleanField(default=False)
    created_by = models.ForeignKey("auth.User", null=True, blank=True, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-start_date", "-id"]
        constraints = [
            models.UniqueConstraint(fields=["space", "number"], name="uniq_contract_number_per_space"),
            models.CheckConstraint(condition=Q(amount_rial__isnull=True) | Q(amount_rial__gte=0), name="contract_amount_nonnegative"),
            models.CheckConstraint(condition=Q(investment_commitment_rial__isnull=True) | Q(investment_commitment_rial__gte=0), name="contract_investment_nonnegative"),
        ]

    @staticmethod
    def _jalali(value):
        import jdatetime
        try:
            year, month, day = (int(part) for part in value.split("/"))
            return jdatetime.date(year, month, day)
        except (ValueError, TypeError, AttributeError):
            return None

    @property
    def duration_days(self):
        start = self._jalali(self.start_date)
        end = self._jalali(self.end_date)
        if not start or not end:
            return None
        return (end.togregorian() - start.togregorian()).days + 1

    @property
    def is_long_term(self):
        days = self.duration_days
        return days is not None and days > 365

    @property
    def remaining_days(self):
        import jdatetime
        end = self._jalali(self.end_date)
        if not end:
            return None
        return (end.togregorian() - jdatetime.date.today().togregorian()).days

    @property
    def time_status(self):
        import jdatetime
        start = self._jalali(self.start_date)
        end = self._jalali(self.end_date)
        if not start or not end:
            return "UNKNOWN"
        today = jdatetime.date.today()
        if today < start:
            return "NOT_STARTED"
        if today > end:
            return "ENDED"
        return "CURRENT"

    @property
    def time_status_label(self):
        return {
            "NOT_STARTED": "شروع‌نشده",
            "CURRENT": "جاری",
            "ENDED": "پایان‌یافته",
            "UNKNOWN": "نیازمند بررسی",
        }[self.time_status]

    def __str__(self):
        return f"{self.number} — فضای {self.space.code}"


class ContractAmendment(models.Model):
    contract = models.ForeignKey(Contract, on_delete=models.PROTECT, related_name="amendments")
    number = models.CharField(max_length=120)
    effective_date = models.CharField(max_length=10)
    description = models.TextField()
    amount_change_rial = models.DecimalField(max_digits=24, decimal_places=0, null=True, blank=True)

    class Meta:
        ordering = ["-effective_date", "-id"]
        constraints = [
            models.UniqueConstraint(fields=["contract", "number"], name="uniq_amendment_number_per_contract"),
        ]



class ContractCirculation(models.Model):
    class State(models.TextChoices):
        RECEIVED = "RECEIVED", "دریافت‌شده"
        READY = "READY", "آماده ارسال"
        SIGNING = "SIGNING", "در گردش امضا"
        RETURNED = "RETURNED", "برگشت برای اصلاح"
        RESEND = "RESEND", "ارسال مجدد"
        READY_APPROVAL = "READY_APPROVAL", "آماده تأیید نهایی"
        APPROVED = "APPROVED", "تأیید نهایی‌شده"
        CONVERTED = "CONVERTED", "تبدیل‌شده به قرارداد رسمی"
        CLOSED_NO_CONTRACT = "CLOSED_NO_CONTRACT", "مختومه بدون قرارداد"

    identity = models.CharField(max_length=30, unique=True, editable=False, blank=True)
    space = models.ForeignKey("properties.CommercialSpace", on_delete=models.PROTECT, related_name="contract_circulations")
    beneficiary = models.ForeignKey(Beneficiary, on_delete=models.PROTECT, related_name="contract_circulations")
    subject = models.CharField(max_length=255)
    operational_start_date = models.CharField(max_length=10, default="1405/07/01")
    state = models.CharField(max_length=30, choices=State.choices, default=State.RECEIVED)
    next_action = models.CharField(max_length=255)
    due_date = models.CharField(max_length=10, blank=True)
    close_reason = models.TextField(blank=True)
    created_by = models.ForeignKey("auth.User", on_delete=models.PROTECT, related_name="created_contract_circulations")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    official_contract = models.OneToOneField(Contract, null=True, blank=True, on_delete=models.PROTECT, related_name="source_circulation")

    class Meta:
        ordering = ["-created_at", "-pk"]
        indexes = [models.Index(fields=["state", "due_date"])]

    def save(self, *args, **kwargs):
        if not self.identity:
            super().save(*args, **kwargs)
            self.identity = f"CC-{self.pk:06d}"
            type(self).objects.filter(pk=self.pk).update(identity=self.identity)
            return
        super().save(*args, **kwargs)

    @property
    def current_custody(self):
        return self.transfers.filter(returned_at__isnull=True).order_by("-delivered_at", "-pk").first()

    def __str__(self):
        return f"{self.identity or 'CC'} — فضای {self.space.code}"


class ContractCustodyTransfer(models.Model):
    class Direction(models.TextChoices):
        OUT = "OUT", "خروج"
        IN = "IN", "ورود"

    circulation = models.ForeignKey(ContractCirculation, on_delete=models.PROTECT, related_name="transfers")
    sender = models.CharField(max_length=255)
    receiver = models.CharField(max_length=255)
    unit = models.CharField(max_length=255)
    delivered_at = models.DateTimeField()
    purpose = models.CharField(max_length=255)
    next_action = models.CharField(max_length=255)
    due_date = models.CharField(max_length=10, blank=True)
    direction = models.CharField(max_length=20, choices=Direction.choices, default=Direction.OUT)
    signature_status = models.CharField(max_length=80, blank=True)
    returned_at = models.DateTimeField(null=True, blank=True)
    return_note = models.TextField(blank=True)
    document = models.ForeignKey("documents.Document", null=True, blank=True, on_delete=models.PROTECT, related_name="contract_custody_transfers")
    created_by = models.ForeignKey("auth.User", on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-delivered_at", "-pk"]
        constraints = [
            models.UniqueConstraint(
                fields=["circulation"],
                condition=models.Q(returned_at__isnull=True),
                name="one_open_contract_custody",
            ),
        ]


class ContractSignatureStep(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "در انتظار ارسال"
        SENT = "SENT", "ارسال‌شده برای امضا"
        SIGNED = "SIGNED", "امضاشده"
        RETURNED = "RETURNED", "برگشت برای اصلاح"
        WAIVED = "WAIVED", "صرف‌نظر از مرحله اختیاری"

    circulation = models.ForeignKey(ContractCirculation, on_delete=models.PROTECT, related_name="signature_steps")
    order = models.PositiveSmallIntegerField()
    role = models.CharField(max_length=120)
    person = models.CharField(max_length=255, blank=True)
    unit = models.CharField(max_length=255)
    required = models.BooleanField(default=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    signed_at = models.DateTimeField(null=True, blank=True)
    returned_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    note = models.TextField(blank=True)
    document = models.ForeignKey("documents.Document", null=True, blank=True, on_delete=models.PROTECT, related_name="contract_signature_steps")
    updated_by = models.ForeignKey("auth.User", on_delete=models.PROTECT)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "pk"]
        constraints = [
            models.UniqueConstraint(fields=["circulation", "order"], name="unique_signature_order"),
        ]


class ContractFinalApproval(models.Model):
    circulation = models.OneToOneField(ContractCirculation, on_delete=models.PROTECT, related_name="final_approval")
    approver = models.ForeignKey("auth.User", on_delete=models.PROTECT)
    approved_at = models.DateTimeField()
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-approved_at", "-pk"]
