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

    @property
    def duration_days(self):
        if not self.start_date or not self.end_date:
            return None
        import jdatetime
        try:
            start = jdatetime.datetime.strptime(self.start_date, "%Y/%m/%d").date().togregorian()
            end = jdatetime.datetime.strptime(self.end_date, "%Y/%m/%d").date().togregorian()
        except ValueError:
            return None
        return (end - start).days + 1

    @property
    def is_long_term(self):
        days = self.duration_days
        return days is not None and days > 365

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
