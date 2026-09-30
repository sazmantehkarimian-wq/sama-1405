"""Central, null-safe Persian presentation rules for every product template."""
from django import template
from django.utils import timezone

from services.dates import normalize_jalali
from services.money import format_rial

register = template.Library()
_FA = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")


@register.filter
def present(value, empty="—"):
    return empty if value is None or value == "" else value


@register.filter
def rial(value):
    return format_rial(value).translate(_FA)


@register.filter
def fa_digits(value):
    return str(value).translate(_FA) if value is not None else "—"


@register.filter
def jalali_datetime(value):
    if not value:
        return "—"
    local = timezone.localtime(value) if timezone.is_aware(value) else value
    return f"{normalize_jalali(local.date())}، {local:%H:%M}".translate(_FA)
