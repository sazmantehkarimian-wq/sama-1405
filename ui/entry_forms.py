from django import forms
from django.core.exceptions import ValidationError

from domains.properties.models import Center, CommercialSpace, MotherProperty, Region
from services.text import normalize_persian_text, normalize_space_code


class BaseNormalizedModelForm(forms.ModelForm):
    def clean(self):
        cleaned = super().clean()
        for name, field in self.fields.items():
            if isinstance(field, (forms.CharField, forms.ChoiceField)) and isinstance(cleaned.get(name), str):
                cleaned[name] = normalize_persian_text(cleaned[name])
        return cleaned


class CommercialSpaceForm(BaseNormalizedModelForm):
    class Meta:
        model = CommercialSpace
        fields = [
            "code", "name", "status", "region", "center", "organizational_scope",
            "asset_type", "area", "address", "physical_details", "current_usage",
            "proposed_activity", "activity_group", "previous_usage", "notes",
        ]
        labels = {
            "code": "کد فضا",
            "name": "نام فضا / مرکز",
            "status": "وضعیت فضا",
            "region": "منطقه شهرداری",
            "center": "مرکز",
            "organizational_scope": "حوزه سازمانی",
            "asset_type": "نوع فضا / دارایی",
            "area": "مساحت اعیان (مترمربع)",
            "address": "نشانی فضای تجاری",
            "physical_details": "مشخصات فیزیکی و امکانات",
            "current_usage": "کاربری اصلی فضای تجاری",
            "proposed_activity": "فعالیت / کاربری پیشنهادی",
            "activity_group": "گروه فعالیت پیشنهادی",
            "previous_usage": "کاربری پیشین",
            "notes": "توضیحات",
        }
        widgets = {
            "code": forms.TextInput(attrs={"inputmode": "numeric", "autocomplete": "off"}),
            "area": forms.NumberInput(attrs={"min": "0", "step": "0.01", "inputmode": "decimal"}),
            "address": forms.Textarea(attrs={"rows": 3}),
            "physical_details": forms.Textarea(attrs={"rows": 3}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["region"].queryset = Region.objects.order_by("code")
        self.fields["center"].queryset = Center.objects.select_related("region").order_by("name")
        self.fields["region"].required = False
        self.fields["center"].required = False
        if self.instance and self.instance.pk:
            self.fields["code"].disabled = True
            self.fields["code"].help_text = "کد فضا پس از ایجاد قابل تغییر نیست."

    def clean_code(self):
        try:
            return normalize_space_code(self.cleaned_data["code"])
        except ValueError as exc:
            raise ValidationError(str(exc)) from exc

    def clean(self):
        cleaned = super().clean()
        region, center = cleaned.get("region"), cleaned.get("center")
        if region and center and center.region_id and center.region_id != region.id:
            self.add_error("center", "مرکز انتخاب‌شده متعلق به منطقه انتخاب‌شده نیست.")
        return cleaned


class MotherPropertyForm(BaseNormalizedModelForm):
    class Meta:
        model = MotherProperty
        fields = [
            "identifier", "name", "region", "center_type", "primary_usage",
            "usage_group", "area", "address", "notes",
        ]
        labels = {
            "identifier": "شناسه ملک مادر",
            "name": "نام ملک / مجموعه",
            "region": "منطقه شهرداری",
            "center_type": "نوع مرکز",
            "primary_usage": "کاربری اصلی",
            "usage_group": "گروه کاربری",
            "area": "مساحت اعیان (مترمربع)",
            "address": "نشانی",
            "notes": "ملاحظات",
        }
        widgets = {
            "area": forms.NumberInput(attrs={"min": "0", "step": "0.01", "inputmode": "decimal"}),
            "address": forms.Textarea(attrs={"rows": 3}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["region"].queryset = Region.objects.order_by("code")
        self.fields["region"].required = False
        if self.instance and self.instance.pk:
            self.fields["identifier"].disabled = True
            self.fields["identifier"].help_text = "شناسه ملک مادر پس از ایجاد قابل تغییر نیست."

    def clean_identifier(self):
        value = normalize_persian_text(self.cleaned_data["identifier"]).upper()
        if not value:
            raise ValidationError("شناسه ملک مادر الزامی است.")
        return value


class RegionForm(BaseNormalizedModelForm):
    class Meta:
        model = Region
        fields = ["code", "name"]
        labels = {"code": "کد منطقه", "name": "نام منطقه"}

    def clean_code(self):
        value = normalize_persian_text(self.cleaned_data["code"])
        if not value.isdigit() or not (1 <= int(value) <= 99):
            raise ValidationError("کد منطقه باید عددی بین 1 تا 99 باشد.")
        return str(int(value))


class CenterForm(BaseNormalizedModelForm):
    class Meta:
        model = Center
        fields = ["name", "region", "is_special"]
        labels = {"name": "نام مرکز", "region": "منطقه", "is_special": "مرکز خاص"}
