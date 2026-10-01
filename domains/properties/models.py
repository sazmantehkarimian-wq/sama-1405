from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models


SPACE_CODE_VALIDATOR = RegexValidator(
    regex=r"^[1-9][0-9]*$",
    message="کد فضا باید فقط عدد صحیح مثبت و بدون صفر ابتدایی باشد.",
)


class Region(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=120)

    class Meta:
        ordering = ["code"]

    def __str__(self):
        return f"{self.code} — {self.name}"


class Center(models.Model):
    name = models.CharField(max_length=255)
    region = models.ForeignKey(Region, null=True, blank=True, on_delete=models.PROTECT)
    is_special = models.BooleanField(default=False)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(fields=["name", "region"], name="uniq_center_region"),
        ]

    def __str__(self):
        return self.name


class MotherProperty(models.Model):
    identifier = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=255)
    region = models.ForeignKey(Region, null=True, blank=True, on_delete=models.PROTECT)
    center_type = models.CharField(max_length=120, blank=True)
    primary_usage = models.CharField(max_length=120, blank=True)
    usage_group = models.CharField(max_length=120, blank=True)
    area = models.DecimalField(
        max_digits=16, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(Decimal("0"))],
    )
    address = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["identifier"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(area__isnull=True) | models.Q(area__gte=0),
                name="mother_property_area_nonnegative",
            ),
        ]

    def save(self, *args, **kwargs):
        if self.pk:
            original = type(self).objects.only("identifier").get(pk=self.pk)
            if original.identifier != self.identifier:
                raise ValidationError("شناسه ملک مادر پس از ایجاد قابل تغییر نیست.")
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.identifier} — {self.name}"


class CommercialSpace(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "فعال"
        OUT_OF_CYCLE = "OUT_OF_CYCLE", "خارج از چرخه"

    code = models.CharField(
        max_length=30, unique=True, db_index=True, validators=[SPACE_CODE_VALIDATOR],
    )
    name = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=Status.choices, db_index=True)
    region = models.ForeignKey(Region, null=True, blank=True, on_delete=models.PROTECT)
    center = models.ForeignKey(Center, null=True, blank=True, on_delete=models.PROTECT)
    organizational_scope = models.CharField(max_length=120, blank=True)
    asset_type = models.CharField(max_length=120, blank=True)
    area = models.DecimalField(
        max_digits=16, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(Decimal("0"))],
    )
    address = models.TextField(blank=True)
    physical_details = models.TextField(blank=True)
    current_usage = models.CharField(max_length=255, blank=True)
    proposed_activity = models.CharField(max_length=255, blank=True)
    activity_group = models.CharField(max_length=255, blank=True)
    previous_usage = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["code"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(area__isnull=True) | models.Q(area__gte=0),
                name="commercial_space_area_nonnegative",
            ),
        ]

    def save(self, *args, **kwargs):
        if self.pk:
            original = type(self).objects.only("code").get(pk=self.pk)
            if original.code != self.code:
                raise ValidationError("کد فضا پس از ایجاد قابل تغییر نیست.")
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.code} — {self.name}"


class CommercialSpaceStatusHistory(models.Model):
    space = models.ForeignKey(
        CommercialSpace, on_delete=models.PROTECT, related_name="status_history",
    )
    previous_state = models.CharField(max_length=20, blank=True)
    new_state = models.CharField(max_length=20)
    effective_date = models.CharField(max_length=10)
    reason = models.TextField()
    responsible_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, on_delete=models.PROTECT,
    )
    source_document = models.ForeignKey(
        "documents.Document", null=True, blank=True, on_delete=models.PROTECT,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]
