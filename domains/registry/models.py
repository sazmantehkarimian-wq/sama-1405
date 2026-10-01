from django.db import models


class CanonicalField(models.Model):
    class Mapping(models.TextChoices):
        MAPPED = "MAPPED"
        DERIVED = "DERIVED"
        REFERENCE_ONLY = "REFERENCE_ONLY"
        DEPRECATED = "DEPRECATED"
        UNRESOLVED = "UNRESOLVED"

    key = models.SlugField(max_length=120, unique=True)
    persian_label = models.CharField(max_length=255)
    aliases = models.JSONField(default=list)
    data_type = models.CharField(max_length=30)
    domain = models.CharField(max_length=60)
    entity = models.CharField(max_length=60)
    meaning = models.TextField()
    authority = models.CharField(max_length=255)
    precedence = models.PositiveSmallIntegerField(default=1)
    nullable = models.BooleanField(default=True)
    required = models.BooleanField(default=False)
    searchable = models.BooleanField(default=False)
    filterable = models.BooleanField(default=False)
    sortable = models.BooleanField(default=False)
    exportable = models.BooleanField(default=True)
    default_visible = models.BooleanField(default=False)
    sensitive = models.BooleanField(default=False)
    deprecated = models.BooleanField(default=False)
    validation_rules = models.JSONField(default=dict)
    mapping_status = models.CharField(max_length=20, choices=Mapping.choices)


class Discrepancy(models.Model):
    class Status(models.TextChoices):
        OPEN = "OPEN", "باز"
        REVIEWING = "REVIEWING", "در بررسی"
        RESOLVED = "RESOLVED", "حل‌شده"

    entity_type = models.CharField(max_length=80)
    entity_key = models.CharField(max_length=120)
    field_key = models.CharField(max_length=120, blank=True)
    observed_value = models.TextField(blank=True)
    expected_value = models.TextField(blank=True)
    reason = models.TextField()
    severity = models.CharField(max_length=20, default="MEDIUM")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    assigned_to = models.ForeignKey(
        "auth.User", null=True, blank=True, on_delete=models.SET_NULL,
    )
    resolution = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]
