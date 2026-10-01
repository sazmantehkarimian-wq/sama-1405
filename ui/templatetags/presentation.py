"""Central, null-safe Persian presentation rules for every product template."""
from django import template
from django.utils import timezone

from services.dates import normalize_jalali
from services.money import format_rial

register = template.Library()
_FA = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")
_ADMIN_LABELS = {
    "OPEN": "در انتظار بررسی", "REVIEWING": "در حال بررسی", "RESOLVED": "حل‌شده",
    "MEDIUM": "متوسط", "HIGH": "زیاد", "LOW": "کم", "CRITICAL": "بحرانی",
    "PENDING": "در انتظار پرداخت", "PAID": "پرداخت‌شده", "UNPAID": "پرداخت‌نشده",
    "DRAFT": "پیش‌نویس", "DONE": "تکمیل‌شده", "CANCELLED": "لغوشده",
    "ACTIVE": "فعال", "OUT_OF_CYCLE": "خارج از چرخه",
    "READY": "آماده", "NOT_READY": "آماده نیست", "REVIEW_REQUIRED": "نیازمند بررسی",
    "CANDIDATE": "کاندیدای مزایده", "NOT_CANDIDATE": "غیرکاندیدا",
}

_REASON_LABELS = {
    "NO_ACTIVE_RULE": "قاعده فعال وجود ندارد", "NO_APPRAISAL": "کارشناسی ثبت نشده است",
    "APPRAISAL_EXPIRED": "اعتبار کارشناسی پایان یافته است", "NO_CONTRACT": "قرارداد جاری ثبت نشده است",
    "CONTRACT_EXPIRING": "قرارداد در آستانه پایان است", "DATA_INCOMPLETE": "اطلاعات پرونده کامل نیست",
    "NOT_CANDIDATE_SPACE_OUT_OF_CYCLE": "فضا خارج از چرخه است", "REVIEW_MISSING_CONTRACT_AMOUNT": "مبلغ قرارداد ثبت نشده است",
    "NOT_CANDIDATE_LEVEL_JOZ": "سطح معامله مشمول مزایده نیست", "CANDIDATE_CONTRACT_WINDOW": "قرارداد در بازه زمانی مصوب پایان است",
    "REVIEW_MISSING_APPRAISAL": "کارشناسی معتبر ثبت نشده است", "NOT_CANDIDATE_OUTSIDE_TIME_WINDOW": "قرارداد خارج از بازه زمانی مصوب است",
    "CANDIDATE_NO_CONTRACT_VALID_APPRAISAL": "بدون قرارداد و دارای کارشناسی معتبر است", "CANDIDATE_STICKY_PREVIOUS_VALID_DECISION": "تصمیم معتبر پیشین حفظ شده است",
}


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


@register.filter
def administrative(value, empty="—"):
    if value is None or value == "":
        return empty
    return _ADMIN_LABELS.get(str(value), str(value)).translate(_FA)


@register.filter
def reason_labels(values):
    return "، ".join(_REASON_LABELS.get(str(value), "نیازمند بررسی کارشناسی") for value in (values or []))
