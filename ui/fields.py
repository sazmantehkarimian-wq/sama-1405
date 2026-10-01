from django import forms

from services.dates import DATE_RE, normalize_jalali
from services.text import normalize_digits


class JalaliDateInput(forms.TextInput):
    input_type = "text"

    def __init__(self, attrs=None):
        base = {
            "inputmode": "numeric",
            "autocomplete": "off",
            "placeholder": "1405/07/01",
            "pattern": r"(13|14)[0-9]{2}/(0[1-9]|1[0-2])/(0[1-9]|[12][0-9]|3[01])",
            "maxlength": "10",
            "dir": "ltr",
        }
        if attrs:
            base.update(attrs)
        super().__init__(base)


class JalaliDateField(forms.CharField):
    widget = JalaliDateInput

    def to_python(self, value):
        value = super().to_python(value)
        if value in self.empty_values:
            return ""
        normalized = normalize_digits(value).strip()
        if not DATE_RE.fullmatch(normalized):
            raise forms.ValidationError("تاریخ شمسی معتبر را دقیقاً با قالب 1405/07/01 وارد کنید.")
        try:
            return normalize_jalali(normalized)
        except (ValueError, TypeError):
            raise forms.ValidationError("تاریخ شمسی معتبر را دقیقاً با قالب 1405/07/01 وارد کنید.")
