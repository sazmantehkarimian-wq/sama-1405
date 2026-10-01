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
    "OUT": "خروج", "IN": "ورود",
    "READY": "آماده", "NOT_READY": "آماده نیست", "REVIEW_REQUIRED": "نیازمند بررسی",
    "CANDIDATE": "کاندیدای مزایده", "NOT_CANDIDATE": "غیرکاندیدا",
}

_REASON_LABELS = {
    "NO_ACTIVE_RULE": "قاعده فعال وجود ندارد", "NO_APPRAISAL": "کارشناسی ثبت نشده است",
    "APPRAISAL_EXPIRED": "اعتبار کارشناسی پایان یافته است", "NO_CONTRACT": "قرارداد جاری ثبت نشده است",
    "CONTRACT_EXPIRING": "قرارداد در آستانه پایان است", "DATA_INCOMPLETE": "اطلاعات پرونده کامل نیست",
    "NOT_CANDIDATE_SPACE_OUT_OF_CYCLE": "فضا خارج از چرخه است", "REVIEW_MISSING_CONTRACT_AMOUNT": "مبلغ قرارداد ثبت نشده است",
    "NOT_CANDIDATE_LEVEL_JOZ": "سطح معامله مشمول مزایده نیست", "CANDIDATE_CONTRACT_WINDOW": "قرارداد در بازه زمانی مصوب پایان است",
    "REVIEW_MISSING_APPRAISAL": "کارشناسی مرجع معتبر ثبت نشده است", "NOT_CANDIDATE_OUTSIDE_TIME_WINDOW": "قرارداد خارج از بازه زمانی مصوب است",
    "NOT_CANDIDATE_CONTRACT_OUTSIDE_WINDOW": "قرارداد خارج از پنجره زمانی مصوب است",
    "ACTION_APPRAISAL_EXPIRES_BEFORE_AUCTION": "کارشناسی تا تاریخ برنامه‌ریزی‌شده مزایده منقضی می‌شود",
    "CONFLICTING_AUTHORIZED_INSTRUCTIONS": "دستورات معتبر متعارض وجود دارد و نیازمند بررسی رسمی است",
    "BLOCKED_BY_MANUAL_EXCLUSION": "بر اساس دستور معتبر از ورود خودکار جلوگیری شده است",
    "INCLUDED_BY_MANUAL_OVERRIDE": "بر اساس دستور معتبر وارد فهرست کاندیدا شده است",
    "CANDIDATE_NO_CONTRACT_VALID_APPRAISAL": "بدون قرارداد و دارای کارشناسی معتبر است", "CANDIDATE_STICKY_PREVIOUS_VALID_DECISION": "تصمیم معتبر پیشین حفظ شده است",
}
_EVENT_LABELS = {
    'SOURCE_HISTORY':'سابقه منبع','BENEFICIARY_HISTORY':'سابقه بهره‌بردار','CONTRACT_HISTORY':'سابقه قرارداد',
    'APPRAISAL_HISTORY':'سابقه کارشناسی','AUCTION_HISTORY':'سابقه مزایده','DECISION_HISTORY':'مصوبه یا دستور',
    'UTILITY_OBLIGATION_HISTORY':'تعهد انشعاب','DOCUMENT_REFERENCE_HISTORY':'مرجع سند','CONTRACT_CREATE':'ثبت قرارداد',
    'CONTRACT_AMENDMENT':'ثبت الحاقیه','APPRAISAL_CREATE':'ثبت کارشناسی','APPRAISAL_FEE_CREATE':'ثبت حق‌الزحمه','APPRAISAL_FEE_TRANSITION':'تغییر وضعیت حق‌الزحمه',
    'UTILITY_RECORD_CREATE':'ثبت مصرف','WORKFLOW_CREATE':'ایجاد فرایند','WORKFLOW_TRANSITION':'تغییر فرایند',
    'COMMISSION_CREATE':'تصمیم کمیسیون','COMMISSION_TRANSITION':'تغییر تصمیم کمیسیون','ALERT_CREATE':'ثبت مورد پیگیری',
    'ALERT_RESOLVE':'مختومه‌سازی مورد پیگیری','FILE_MOVEMENT_CREATE':'تحویل فیزیکی پرونده','FILE_MOVEMENT_RETURN':'بازگشت پرونده','SPACE_STATUS_TRANSITION':'تغییر وضعیت فضا',
    'AUCTION_EVALUATE':'بررسی آمادگی مزایده','AUCTION_LOT_ADD':'افزودن به دوره مزایده',
    'AUCTION_INSTRUCTION_CREATE':'ثبت دستور مؤثر بر مزایده',
    'COMMISSION_SESSION_CREATE':'ثبت جلسه کمیسیون','COMMISSION_CASE_CREATE':'طرح موضوع کمیسیون',
    'COMMISSION_DECISION_CREATE':'ثبت تصمیم کمیسیون','COMMISSION_FOLLOWUP_CREATE':'ایجاد پیگیری مصوبه',
    'COMMISSION_FOLLOWUP_TRANSITION':'تغییر وضعیت پیگیری مصوبه',
    'DOCUMENT_UPLOAD':'بارگذاری سند',
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


@register.filter
def event_label(value):
    return _EVENT_LABELS.get(str(value), 'سابقه پرونده')
