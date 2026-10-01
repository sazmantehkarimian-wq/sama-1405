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


class PropertyReferenceValue(models.Model):
    class Category(models.TextChoices):
        STATUS = "STATUS", "وضعیت جاری ملک"
        CENTER_TYPE = "CENTER_TYPE", "نوع مرکز / مکان"
        USAGE = "USAGE", "نوع کاربری"
        USAGE_GROUP = "USAGE_GROUP", "گروه کاربری"
        ORG_UNIT = "ORG_UNIT", "واحد / مرکز سازمانی"
        USAGE_STATUS = "USAGE_STATUS", "وضعیت بهره‌برداری"
        OWNERSHIP_STATUS = "OWNERSHIP_STATUS", "وضعیت مستند مالکیت"

    category = models.CharField(max_length=40, choices=Category.choices)
    value = models.CharField(max_length=120)
    active = models.BooleanField(default=True)
    sort_order = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["category", "sort_order", "value"]
        constraints = [
            models.UniqueConstraint(fields=["category", "value"], name="uniq_property_reference_category_value"),
        ]

    def __str__(self):
        return self.value


class MotherProperty(models.Model):
    class Presence(models.TextChoices):
        YES = "YES", "دارد"
        NO = "NO", "ندارد"
        UNKNOWN = "UNKNOWN", "نامشخص"

    class OwnerType(models.TextChoices):
        NATURAL = "NATURAL", "حقیقی"
        LEGAL = "LEGAL", "حقوقی"
        ORGANIZATIONAL = "ORGANIZATIONAL", "سازمانی"
        UNKNOWN = "UNKNOWN", "نامشخص"

    identifier = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=255)
    region = models.ForeignKey(Region, null=True, blank=True, on_delete=models.PROTECT)
    current_status = models.CharField(max_length=120, blank=True)
    center_type = models.CharField(max_length=120, blank=True)
    primary_usage = models.CharField(max_length=120, blank=True)
    usage_group = models.CharField(max_length=120, blank=True)
    holder_unit = models.CharField(max_length=255, blank=True)
    land_area = models.DecimalField(
        max_digits=16, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(Decimal("0"))],
    )
    area = models.DecimalField(
        max_digits=16, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(Decimal("0"))],
    )
    address = models.TextField(blank=True)
    ownership_document_status = models.CharField(max_length=120, blank=True)
    owner_name = models.CharField(max_length=255, blank=True)
    owner_type = models.CharField(max_length=20, choices=OwnerType.choices, blank=True)
    ownership_notes = models.TextField(blank=True)
    has_utilities = models.CharField(max_length=10, choices=Presence.choices, default=Presence.UNKNOWN)
    electricity_presence = models.CharField(max_length=10, choices=Presence.choices, default=Presence.UNKNOWN)
    water_presence = models.CharField(max_length=10, choices=Presence.choices, default=Presence.UNKNOWN)
    gas_presence = models.CharField(max_length=10, choices=Presence.choices, default=Presence.UNKNOWN)
    other_utilities = models.CharField(max_length=255, blank=True)
    utility_notes = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.PROTECT,
        related_name="created_mother_properties",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.PROTECT,
        related_name="updated_mother_properties",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["identifier"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(area__isnull=True) | models.Q(area__gte=0),
                name="mother_property_area_nonnegative",
            ),
            models.CheckConstraint(
                condition=models.Q(land_area__isnull=True) | models.Q(land_area__gte=0),
                name="mother_property_land_area_nonnegative",
            ),
        ]

    def save(self, *args, **kwargs):
        if self.pk:
            original = type(self).objects.only("identifier").get(pk=self.pk)
            if original.identifier != self.identifier:
                raise ValidationError("شناسه ملک مادر پس از ایجاد قابل تغییر نیست.")
        return super().save(*args, **kwargs)

    @property
    def current_usage_record(self):
        return self.usage_history.filter(end_date="").order_by("-start_date", "-pk").first()

    @property
    def completeness_reasons(self):
        reasons = []
        if not self.current_status:
            reasons.append("وضعیت جاری ثبت نشده")
        if self.area is None:
            reasons.append("مساحت اعیان ثبت نشده")
        if not self.ownership_document_status:
            reasons.append("وضعیت مالکیت ثبت نشده")
        if self.water_presence == self.Presence.UNKNOWN:
            reasons.append("وضعیت انشعاب آب نامشخص است")
        if self.electricity_presence == self.Presence.UNKNOWN:
            reasons.append("وضعیت انشعاب برق نامشخص است")
        if self.gas_presence == self.Presence.UNKNOWN:
            reasons.append("وضعیت انشعاب گاز نامشخص است")
        return reasons

    @property
    def completeness_status(self):
        return "کامل" if not self.completeness_reasons else "نیازمند تکمیل"

    def __str__(self):
        return f"{self.identifier} — {self.name}"


class MotherPropertyOwnership(models.Model):
    property = models.ForeignKey(MotherProperty, on_delete=models.PROTECT, related_name="ownership_history")
    owner_name = models.CharField(max_length=255)
    owner_type = models.CharField(max_length=20, choices=MotherProperty.OwnerType.choices)
    share_percent = models.DecimalField(max_digits=7, decimal_places=4, null=True, blank=True)
    start_date = models.CharField(max_length=10, blank=True)
    end_date = models.CharField(max_length=10, blank=True)
    basis = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-start_date", "-pk"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(share_percent__isnull=True) | (models.Q(share_percent__gte=0) & models.Q(share_percent__lte=100)),
                name="mother_owner_share_range",
            ),
        ]


class MotherPropertyOwnershipDocument(models.Model):
    class RecordStatus(models.TextChoices):
        ACTIVE = "ACTIVE", "فعال"
        VOID = "VOID", "باطل"
        ERROR = "ERROR", "ثبت اشتباه"

    property = models.ForeignKey(MotherProperty, on_delete=models.PROTECT, related_name="ownership_documents")
    document_type = models.CharField(max_length=120)
    document_number = models.CharField(max_length=120, blank=True)
    document_date = models.CharField(max_length=10, blank=True)
    notary_number = models.CharField(max_length=80, blank=True)
    notary_name = models.CharField(max_length=255, blank=True)
    main_plate = models.CharField(max_length=80, blank=True)
    sub_plate = models.CharField(max_length=80, blank=True)
    registration_section = models.CharField(max_length=120, blank=True)
    documented_area = models.DecimalField(max_digits=16, decimal_places=2, null=True, blank=True)
    documented_owner_name = models.CharField(max_length=255, blank=True)
    owner_type = models.CharField(max_length=20, choices=MotherProperty.OwnerType.choices, blank=True)
    description = models.TextField(blank=True)
    document = models.ForeignKey("documents.Document", null=True, blank=True, on_delete=models.PROTECT, related_name="mother_property_ownership_records")
    status = models.CharField(max_length=20, choices=RecordStatus.choices, default=RecordStatus.ACTIVE)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-document_date", "-pk"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(documented_area__isnull=True) | models.Q(documented_area__gte=0),
                name="mother_ownership_doc_area_nonnegative",
            ),
        ]


class MotherPropertyUsageHistory(models.Model):
    property = models.ForeignKey(MotherProperty, on_delete=models.PROTECT, related_name="usage_history")
    usage_status = models.CharField(max_length=120)
    holder_type = models.CharField(max_length=120, blank=True)
    holder_unit = models.CharField(max_length=255, blank=True)
    beneficiary_name = models.CharField(max_length=255, blank=True)
    beneficiary_type = models.CharField(max_length=120, blank=True)
    start_date = models.CharField(max_length=10)
    end_date = models.CharField(max_length=10, blank=True)
    basis = models.CharField(max_length=255, blank=True)
    contract_reference = models.CharField(max_length=255, blank=True)
    document = models.ForeignKey("documents.Document", null=True, blank=True, on_delete=models.PROTECT, related_name="mother_property_usage_records")
    termination_reason = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-start_date", "-pk"]
        constraints = [
            models.UniqueConstraint(
                fields=["property"],
                condition=models.Q(end_date=""),
                name="one_open_mother_property_usage",
            ),
        ]


class MotherPropertyCorrespondence(models.Model):
    class FollowUpStatus(models.TextChoices):
        OPEN = "OPEN", "باز"
        DONE = "DONE", "انجام‌شده"
        CLOSED = "CLOSED", "مختومه"
        REVIEW_REQUIRED = "REVIEW_REQUIRED", "نیازمند بررسی"

    property = models.ForeignKey(MotherProperty, on_delete=models.PROTECT, related_name="correspondence")
    document_type = models.CharField(max_length=120)
    number = models.CharField(max_length=120, blank=True)
    document_date = models.CharField(max_length=10, blank=True)
    subject = models.CharField(max_length=255)
    sender = models.CharField(max_length=255, blank=True)
    recipient = models.CharField(max_length=255, blank=True)
    organizational_unit = models.CharField(max_length=255, blank=True)
    summary = models.TextField(blank=True)
    needs_follow_up = models.BooleanField(default=False)
    responsible = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.PROTECT, related_name="mother_property_correspondence")
    due_date = models.CharField(max_length=10, blank=True)
    follow_up_status = models.CharField(max_length=30, choices=FollowUpStatus.choices, default=FollowUpStatus.OPEN)
    document = models.ForeignKey("documents.Document", null=True, blank=True, on_delete=models.PROTECT, related_name="mother_property_correspondence")
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.PROTECT, related_name="created_mother_property_correspondence")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-document_date", "-pk"]


class MotherPropertyNote(models.Model):
    property = models.ForeignKey(MotherProperty, on_delete=models.PROTECT, related_name="internal_notes")
    subject = models.CharField(max_length=255, blank=True)
    text = models.TextField()
    active = models.BooleanField(default=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-pk"]


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
