from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

ZERO = Decimal("0")
HUNDRED = Decimal("100")


class UtilityAccount(models.Model):
    class Type(models.TextChoices):
        ELECTRICITY = "ELECTRICITY", "برق"
        WATER = "WATER", "آب"
        GAS = "GAS", "گاز"
        TELEPHONE = "TELEPHONE", "تلفن"
        OTHER = "OTHER", "سایر"

    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "فعال"
        DISCONNECTED = "DISCONNECTED", "قطع"
        INACTIVE = "INACTIVE", "غیرفعال"
        TRANSFER = "TRANSFER", "در حال انتقال"
        REVIEW = "REVIEW", "نیازمند بررسی"

    utility_type = models.CharField(max_length=20, choices=Type.choices, db_index=True)
    title = models.CharField(max_length=255)
    account_number = models.CharField(max_length=120, blank=True, db_index=True)
    bill_identifier = models.CharField(max_length=120, blank=True, db_index=True)
    payment_identifier = models.CharField(max_length=120, blank=True)
    meter_number = models.CharField(max_length=120, blank=True, db_index=True)
    ownership = models.CharField(max_length=120, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE, db_index=True)
    region = models.ForeignKey("properties.Region", null=True, blank=True, on_delete=models.PROTECT, related_name="utility_accounts")
    center = models.ForeignKey("properties.Center", null=True, blank=True, on_delete=models.PROTECT, related_name="utility_accounts")
    mother_property = models.ForeignKey("properties.MotherProperty", null=True, blank=True, on_delete=models.PROTECT, related_name="utility_accounts")
    dedicated_space = models.ForeignKey("properties.CommercialSpace", null=True, blank=True, on_delete=models.PROTECT, related_name="dedicated_utility_accounts")
    technical_capacity = models.CharField(max_length=255, blank=True)
    service_address = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.PROTECT, related_name="created_utility_accounts")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["utility_type", "region__code", "title", "id"]
        constraints = [models.UniqueConstraint(fields=["utility_type", "account_number"], condition=~models.Q(account_number=""), name="uniq_utility_type_account_number")]

    def __str__(self):
        return f"{self.get_utility_type_display()} - {self.title}"


class UtilityAllocationPolicy(models.Model):
    class Method(models.TextChoices):
        METHOD3 = "METHOD3", "روش سوم — ترکیبی نهایی"

    account = models.OneToOneField(UtilityAccount, on_delete=models.PROTECT, related_name="allocation_policy")
    method = models.CharField(max_length=20, choices=Method.choices, default=Method.METHOD3)
    beneficiary_percent = models.DecimalField(max_digits=7, decimal_places=4, default=ZERO)
    organization_percent = models.DecimalField(max_digits=7, decimal_places=4, default=HUNDRED)
    season_factor = models.DecimalField(max_digits=10, decimal_places=6, default=Decimal("1"))
    editable = models.BooleanField(default=True)
    approved_reference = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.PROTECT, related_name="updated_utility_policies")
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        super().clean()
        op = self.beneficiary_percent or ZERO
        org = self.organization_percent or ZERO
        if op < ZERO or org < ZERO or op > HUNDRED or org > HUNDRED:
            raise ValidationError("درصد سهم سازمان و بهره‌بردار باید بین صفر و ۱۰۰ باشد.")
        if not (op == ZERO and org == ZERO) and (op + org).quantize(Decimal("0.0001")) != HUNDRED:
            raise ValidationError("جمع سهم سازمان و بهره‌بردار باید دقیقاً ۱۰۰ درصد باشد؛ حالت ۰/۰ فقط برای واحد فاقد داده مجاز است.")
        if self.season_factor <= ZERO:
            raise ValidationError("ضریب فصل باید بزرگ‌تر از صفر باشد.")

    def __str__(self):
        return f"{self.account} | بهره‌بردار {self.beneficiary_percent}% / سازمان {self.organization_percent}%"


class UtilitySpaceProfile(models.Model):
    class SpecialModel(models.TextChoices):
        NORMAL = "NORMAL", "عادی"
        EQUIPMENT = "EQUIPMENT", "تجهیزات‌محور"
        OPEN_AREA = "OPEN_AREA", "فضای باز"
        LIGHTING = "LIGHTING", "روشنایی محوطه"
        WATER_FEATURE = "WATER_FEATURE", "محوطه آبی"
        OTHER = "OTHER", "سایر"

    account = models.ForeignKey(UtilityAccount, on_delete=models.PROTECT, related_name="space_profiles")
    space = models.ForeignKey("properties.CommercialSpace", on_delete=models.PROTECT, related_name="utility_profiles")
    included = models.BooleanField(default=True)
    consumption_category = models.CharField(max_length=255, blank=True)
    special_model = models.CharField(max_length=20, choices=SpecialModel.choices, default=SpecialModel.NORMAL)
    area_override = models.DecimalField(max_digits=16, decimal_places=3, null=True, blank=True)
    eui = models.DecimalField(max_digits=16, decimal_places=6, default=ZERO)
    hours_factor = models.DecimalField(max_digits=16, decimal_places=6, default=Decimal("1"))
    category_factor = models.DecimalField(max_digits=16, decimal_places=6, default=Decimal("1"))
    row_factor = models.DecimalField(max_digits=16, decimal_places=6, default=Decimal("1"))
    special_consumption = models.DecimalField(max_digits=24, decimal_places=6, default=ZERO)
    manual_share_percent = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    manual_share_locked = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.PROTECT, related_name="updated_utility_profiles")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["account", "space"], name="uniq_utility_account_space_profile")]
        ordering = ["space__code"]

    def clean(self):
        super().clean()
        if self.manual_share_percent is not None and not (ZERO <= self.manual_share_percent <= HUNDRED):
            raise ValidationError("درصد دستی کدفضا باید بین صفر و ۱۰۰ باشد.")
        for value, label in [(self.eui, "EUI"), (self.hours_factor, "ضریب ساعت"), (self.category_factor, "ضریب دسته"), (self.row_factor, "ضریب ردیف"), (self.special_consumption, "مصرف ویژه")]:
            if value is not None and value < ZERO:
                raise ValidationError(f"{label} نمی‌تواند منفی باشد.")

    @property
    def effective_area(self):
        if self.area_override is not None:
            return self.area_override
        return self.space.area or ZERO

    def __str__(self):
        return f"{self.account} / کد {self.space.code}"


class UtilityBill(models.Model):
    class Status(models.TextChoices):
        DRAFT = "DRAFT", "پیش‌نویس"
        CALCULATED = "CALCULATED", "محاسبه‌شده"
        PARTIAL = "PARTIAL", "پرداخت ناقص"
        PAID = "PAID", "پرداخت‌شده"
        OVERDUE = "OVERDUE", "سررسیدگذشته"
        CANCELLED = "CANCELLED", "لغوشده"

    account = models.ForeignKey(UtilityAccount, on_delete=models.PROTECT, related_name="bills")
    period_start = models.CharField(max_length=10, blank=True, db_index=True)
    period_end = models.CharField(max_length=10, blank=True, db_index=True)
    bill_date = models.CharField(max_length=10, blank=True)
    due_date = models.CharField(max_length=10, blank=True, db_index=True)
    total_consumption = models.DecimalField(max_digits=24, decimal_places=6, null=True, blank=True)
    amount_rial = models.DecimalField(max_digits=24, decimal_places=0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT, db_index=True)
    organization_percent_effective = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    beneficiary_percent_effective = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    organization_amount_rial = models.DecimalField(max_digits=24, decimal_places=0, null=True, blank=True)
    beneficiary_amount_rial = models.DecimalField(max_digits=24, decimal_places=0, null=True, blank=True)
    calculation_snapshot = models.JSONField(default=dict, blank=True)
    attachment = models.FileField(upload_to="utilities/bills/%Y/%m/", blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.PROTECT, related_name="created_utility_bills")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-period_end", "-id"]

    def clean(self):
        super().clean()
        if self.amount_rial < ZERO:
            raise ValidationError("مبلغ قبض نمی‌تواند منفی باشد.")

    def __str__(self):
        return f"{self.account} | {self.period_start} تا {self.period_end}"


class UtilityMeterReading(models.Model):
    bill = models.ForeignKey(UtilityBill, on_delete=models.CASCADE, related_name="meter_readings")
    profile = models.ForeignKey(UtilitySpaceProfile, on_delete=models.PROTECT, related_name="meter_readings")
    measured_consumption = models.DecimalField(max_digits=24, decimal_places=6)
    reading_date = models.CharField(max_length=10, blank=True)
    meter_number = models.CharField(max_length=120, blank=True)
    is_valid = models.BooleanField(default=True)
    source_note = models.TextField(blank=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["bill", "profile"], name="uniq_bill_profile_meter_reading")]

    def clean(self):
        super().clean()
        if self.measured_consumption < ZERO:
            raise ValidationError("مصرف اندازه‌گیری‌شده نمی‌تواند منفی باشد.")
        if self.profile_id and self.bill_id and self.profile.account_id != self.bill.account_id:
            raise ValidationError("زیرکنتور باید متعلق به همان انشعاب قبض باشد.")


class UtilityAllocation(models.Model):
    class Basis(models.TextChoices):
        MEASURED = "MEASURED", "زیرکنتور / اندازه‌گیری واقعی"
        EQUIPMENT = "EQUIPMENT", "مصرف ویژه تجهیزات"
        METHOD3 = "METHOD3", "روش سوم"
        MANUAL = "MANUAL", "درصد دستی قفل‌شده"

    bill = models.ForeignKey(UtilityBill, on_delete=models.CASCADE, related_name="allocations")
    profile = models.ForeignKey(UtilitySpaceProfile, on_delete=models.PROTECT, related_name="allocations")
    basis = models.CharField(max_length=20, choices=Basis.choices)
    consumption_weight = models.DecimalField(max_digits=30, decimal_places=8, default=ZERO)
    share_percent = models.DecimalField(max_digits=12, decimal_places=8)
    amount_rial = models.DecimalField(max_digits=24, decimal_places=0)
    overridden = models.BooleanField(default=False)
    override_reason = models.TextField(blank=True)
    snapshot = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["bill", "profile"], name="uniq_bill_profile_allocation")]
        ordering = ["-share_percent", "profile__space__code"]


class UtilityPayment(models.Model):
    class Payer(models.TextChoices):
        ORGANIZATION = "ORGANIZATION", "سازمان"
        BENEFICIARY = "BENEFICIARY", "بهره‌بردار"
        MIXED = "MIXED", "مشترک"

    bill = models.ForeignKey(UtilityBill, on_delete=models.PROTECT, related_name="payments")
    allocation = models.ForeignKey(UtilityAllocation, null=True, blank=True, on_delete=models.PROTECT, related_name="payments")
    payer = models.CharField(max_length=20, choices=Payer.choices)
    amount_rial = models.DecimalField(max_digits=24, decimal_places=0)
    payment_date = models.CharField(max_length=10)
    reference = models.CharField(max_length=255, blank=True)
    attachment = models.FileField(upload_to="utilities/payments/%Y/%m/", blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.PROTECT, related_name="created_utility_payments")
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        super().clean()
        if self.amount_rial <= ZERO:
            raise ValidationError("مبلغ پرداخت باید بزرگ‌تر از صفر باشد.")
        if self.allocation_id and self.allocation.bill_id != self.bill_id:
            raise ValidationError("سهم انتخاب‌شده متعلق به این قبض نیست.")


class UtilityChangeLog(models.Model):
    entity_type = models.CharField(max_length=80, db_index=True)
    entity_id = models.CharField(max_length=80, db_index=True)
    action = models.CharField(max_length=80)
    previous_state = models.JSONField(null=True, blank=True)
    new_state = models.JSONField(null=True, blank=True)
    reason = models.TextField(blank=True)
    responsible = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="utility_change_logs")
    occurred_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-occurred_at", "-id"]
