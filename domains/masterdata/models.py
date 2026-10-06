from django.core.validators import RegexValidator
from django.db import models


jalali_date_validator = RegexValidator(
    regex=r"^[0-9۰-۹]{4}/[0-9۰-۹]{2}/[0-9۰-۹]{2}$",
    message="تاریخ باید به صورت ۱۴۰۵/۰۷/۱۵ یا 1405/07/15 وارد شود.",
)


class ReferenceCategory(models.Model):
    class Kind(models.TextChoices):
        USAGE = "USAGE", "گروه کاربری"
        ACTIVITY = "ACTIVITY", "نوع فعالیت"
        CENTER_TYPE = "CENTER_TYPE", "نوع مرکز"
        ORGANIZATIONAL_SCOPE = "ORGANIZATIONAL_SCOPE", "حوزه سازمانی"

    kind = models.CharField(max_length=30, choices=Kind.choices, db_index=True)
    code = models.SlugField(max_length=80)
    name = models.CharField(max_length=180)
    aliases = models.JSONField(default=list, blank=True)
    sort_order = models.PositiveIntegerField(default=100)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["kind", "code"], name="uniq_masterdata_category_kind_code"),
            models.UniqueConstraint(fields=["kind", "name"], name="uniq_masterdata_category_kind_name"),
        ]
        ordering = ["kind", "sort_order", "name"]

    def __str__(self):
        return self.name


class OrganizationUnit(models.Model):
    class UnitType(models.TextChoices):
        ORGANIZATION = "ORGANIZATION", "سازمان"
        DEPUTY = "DEPUTY", "معاونت"
        MANAGEMENT = "MANAGEMENT", "مدیریت"
        DEPARTMENT = "DEPARTMENT", "اداره"
        REGION = "REGION", "منطقه"
        CENTER = "CENTER", "مرکز"
        SPECIAL_CENTER = "SPECIAL_CENTER", "مرکز خاص"
        OTHER = "OTHER", "سایر"

    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    unit_type = models.CharField(max_length=30, choices=UnitType.choices, db_index=True)
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.PROTECT, related_name="children")
    region = models.ForeignKey("properties.Region", null=True, blank=True, on_delete=models.PROTECT, related_name="masterdata_units")
    center = models.ForeignKey("properties.Center", null=True, blank=True, on_delete=models.PROTECT, related_name="masterdata_units")
    phone = models.CharField(max_length=80, blank=True)
    extension = models.CharField(max_length=30, blank=True)
    address = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ["unit_type", "name"]

    def __str__(self):
        return self.name


class OrganizationPerson(models.Model):
    full_name = models.CharField(max_length=180, db_index=True)
    mobile = models.CharField(max_length=40, blank=True)
    phone = models.CharField(max_length=80, blank=True)
    extension = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["full_name", "id"]

    def __str__(self):
        return self.full_name


class PositionAssignment(models.Model):
    person = models.ForeignKey(OrganizationPerson, on_delete=models.PROTECT, related_name="assignments")
    unit = models.ForeignKey(OrganizationUnit, on_delete=models.PROTECT, related_name="assignments")
    title = models.CharField(max_length=180, db_index=True)
    start_date = models.CharField(max_length=10, blank=True, validators=[jalali_date_validator])
    end_date = models.CharField(max_length=10, blank=True, validators=[jalali_date_validator])
    is_current = models.BooleanField(default=True, db_index=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-is_current", "unit__name", "title", "person__full_name"]
        indexes = [models.Index(fields=["unit", "is_current"]), models.Index(fields=["title", "is_current"])]

    def __str__(self):
        return f"{self.person} — {self.title} — {self.unit}"
