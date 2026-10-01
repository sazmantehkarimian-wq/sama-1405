from django import forms
from django.core.exceptions import ValidationError

from domains.contracts.models import Beneficiary, Contract
from domains.operations.models import Appraiser, AppraisalNotification
from domains.properties.models import Center, CommercialSpace, MotherProperty, Region
from services.text import normalize_digits, normalize_persian_text, normalize_space_code
from ui.fields import JalaliDateField


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
            self.fields["status"].disabled = True
            self.fields["status"].help_text = "تغییر وضعیت فقط از گردش کنترل‌شده وضعیت پرونده انجام می‌شود."

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



class BeneficiaryForm(BaseNormalizedModelForm):
    birth_date = JalaliDateField(label="تاریخ تولد", required=False)

    class Meta:
        model = Beneficiary
        fields = [
            "kind", "first_name", "last_name", "identity_number", "father_name",
            "birth_certificate_number", "birth_date", "legal_name",
            "registration_number", "legal_entity_type", "economic_code",
            "representative_name", "mobile", "phone", "address", "postal_code",
        ]
        labels = {
            "kind": "نوع بهره‌بردار",
            "first_name": "نام",
            "last_name": "نام خانوادگی",
            "identity_number": "کد ملی / شناسه ملی",
            "father_name": "نام پدر",
            "birth_certificate_number": "شماره شناسنامه",
            "legal_name": "نام کامل شخصیت حقوقی",
            "registration_number": "شماره ثبت",
            "legal_entity_type": "نوع شخصیت حقوقی",
            "economic_code": "کد اقتصادی",
            "representative_name": "نماینده / مسئول معرفی‌شده",
            "mobile": "تلفن همراه",
            "phone": "تلفن ثابت",
            "address": "نشانی",
            "postal_code": "کدپستی",
        }
        widgets = {
            "identity_number": forms.TextInput(attrs={"inputmode": "numeric", "autocomplete": "off"}),
            "mobile": forms.TextInput(attrs={"inputmode": "tel"}),
            "phone": forms.TextInput(attrs={"inputmode": "tel"}),
            "address": forms.Textarea(attrs={"rows": 3}),
        }

    def clean_identity_number(self):
        value = normalize_digits(self.cleaned_data.get("identity_number", "")).strip()
        if not value:
            return ""
        if not value.isdigit():
            raise ValidationError("کد ملی / شناسه ملی باید فقط عدد باشد.")
        kind = self.data.get("kind") or getattr(self.instance, "kind", "")
        expected = 10 if kind == Beneficiary.Kind.NATURAL else 11
        if len(value) != expected:
            label = "کد ملی" if expected == 10 else "شناسه ملی"
            raise ValidationError(f"{label} باید دقیقاً {expected} رقم باشد.")
        duplicate = Beneficiary.objects.filter(identity_number=value)
        if self.instance and self.instance.pk:
            duplicate = duplicate.exclude(pk=self.instance.pk)
        if duplicate.exists():
            raise ValidationError("پرونده‌ای با این شناسه قبلاً ثبت شده است.")
        return value

    def clean_mobile(self):
        value = normalize_digits(self.cleaned_data.get("mobile", "")).strip()
        if value and (not value.isdigit() or len(value) not in (10, 11)):
            raise ValidationError("شماره همراه باید عدد معتبر باشد.")
        return value

    def clean_postal_code(self):
        value = normalize_digits(self.cleaned_data.get("postal_code", "")).strip()
        if value and (not value.isdigit() or len(value) != 10):
            raise ValidationError("کدپستی باید ۱۰ رقم باشد.")
        return value

    def clean(self):
        cleaned = super().clean()
        kind = cleaned.get("kind")
        if kind == Beneficiary.Kind.NATURAL:
            if not cleaned.get("first_name"):
                self.add_error("first_name", "نام شخص حقیقی الزامی است.")
            if not cleaned.get("last_name"):
                self.add_error("last_name", "نام خانوادگی شخص حقیقی الزامی است.")
            cleaned["legal_name"] = ""
        elif kind == Beneficiary.Kind.LEGAL:
            if not cleaned.get("legal_name"):
                self.add_error("legal_name", "نام کامل شخصیت حقوقی الزامی است.")
            cleaned["first_name"] = ""
            cleaned["last_name"] = ""
        return cleaned

    def save(self, commit=True):
        instance = super().save(commit=False)
        if instance.kind == Beneficiary.Kind.NATURAL:
            instance.name = normalize_persian_text(f"{instance.first_name} {instance.last_name}")
        else:
            instance.name = normalize_persian_text(instance.legal_name)
        instance.contact = instance.mobile or instance.phone
        if commit:
            instance.save()
            self.save_m2m()
        return instance


class ContractEntryForm(forms.Form):
    beneficiary = forms.ModelChoiceField(
        label="بهره‌بردار",
        queryset=Beneficiary.objects.none(),
        empty_label="انتخاب بهره‌بردار ثبت‌شده",
    )
    number = forms.CharField(label="شماره قرارداد", max_length=120)
    subject = forms.CharField(label="موضوع قرارداد", max_length=255, required=False)
    signed_date = JalaliDateField(label="تاریخ امضا", required=False)
    start_date = JalaliDateField(label="تاریخ شروع", required=True)
    end_date = JalaliDateField(label="تاریخ پایان", required=True)
    amount_rial = forms.DecimalField(label="مبلغ قرارداد (ریال)", required=False, min_value=0, decimal_places=0, max_digits=24)
    investment_commitment_rial = forms.DecimalField(label="تعهد سرمایه‌گذاری (ریال)", required=False, min_value=0, decimal_places=0, max_digits=24)
    status = forms.CharField(label="وضعیت حقوقی", max_length=80, required=False, help_text="فقط در صورت وجود وضعیت حقوقی واقعی ثبت شود.")
    signed_state = forms.CharField(label="وضعیت امضا", max_length=80, required=False)
    notes = forms.CharField(label="توضیحات", required=False, widget=forms.Textarea(attrs={"rows": 3}))

    def __init__(self, *args, space=None, **kwargs):
        self.space = space
        super().__init__(*args, **kwargs)
        self.fields["beneficiary"].queryset = Beneficiary.objects.filter(archived_at__isnull=True).order_by("name")
        for key in ("amount_rial", "investment_commitment_rial"):
            self.fields[key].widget.attrs.update({"inputmode": "numeric", "min": "0"})

    def clean_number(self):
        value = normalize_persian_text(self.cleaned_data["number"])
        if self.space and Contract.objects.filter(space=self.space, number=value).exists():
            raise ValidationError("این شماره قرارداد برای این کد فضا قبلاً ثبت شده است.")
        return value

    def clean(self):
        cleaned = super().clean()
        start, end = cleaned.get("start_date"), cleaned.get("end_date")
        if start and end and start > end:
            self.add_error("end_date", "تاریخ پایان نمی‌تواند قبل از تاریخ شروع باشد.")
        return cleaned



class AppraiserForm(BaseNormalizedModelForm):
    class Meta:
        model = Appraiser
        fields = [
            "first_name", "last_name", "national_id", "license_number",
            "specialty", "professional_authority", "mobile", "phone",
            "address", "email", "collaboration_status", "notes",
        ]
        labels = {
            "first_name": "نام",
            "last_name": "نام خانوادگی",
            "national_id": "کد ملی",
            "license_number": "شماره پروانه / شناسه حرفه‌ای",
            "specialty": "رشته / صلاحیت",
            "professional_authority": "مرجع حرفه‌ای",
            "mobile": "شماره همراه",
            "phone": "تلفن",
            "address": "نشانی",
            "email": "ایمیل",
            "collaboration_status": "وضعیت همکاری",
            "notes": "توضیحات",
        }
        widgets = {
            "national_id": forms.TextInput(attrs={"inputmode": "numeric"}),
            "mobile": forms.TextInput(attrs={"inputmode": "tel"}),
            "phone": forms.TextInput(attrs={"inputmode": "tel"}),
            "address": forms.Textarea(attrs={"rows": 3}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def clean_national_id(self):
        value = normalize_digits(self.cleaned_data.get("national_id", "")).strip()
        if value and (not value.isdigit() or len(value) != 10):
            raise ValidationError("کد ملی کارشناس باید ۱۰ رقم باشد.")
        duplicate = Appraiser.objects.filter(national_id=value) if value else Appraiser.objects.none()
        if self.instance and self.instance.pk:
            duplicate = duplicate.exclude(pk=self.instance.pk)
        if duplicate.exists():
            raise ValidationError("کارشناس دیگری با این کد ملی ثبت شده است.")
        return value

    def clean_license_number(self):
        value = normalize_persian_text(self.cleaned_data.get("license_number", ""))
        duplicate = Appraiser.objects.filter(license_number=value) if value else Appraiser.objects.none()
        if self.instance and self.instance.pk:
            duplicate = duplicate.exclude(pk=self.instance.pk)
        if duplicate.exists():
            raise ValidationError("کارشناس دیگری با این شماره پروانه ثبت شده است.")
        return value


class AppraisalEntryForm(forms.Form):
    appraiser = forms.ModelChoiceField(
        label="کارشناس",
        queryset=Appraiser.objects.none(),
        empty_label="انتخاب کارشناس ثبت‌شده",
    )
    sequence = forms.CharField(label="نوبت / شناسه داخلی", max_length=20, required=False)
    notification_number = forms.CharField(label="شماره ابلاغ", max_length=120, required=False)
    notification_date = JalaliDateField(label="تاریخ ابلاغ", required=False)
    notification_recipient = forms.ChoiceField(
        label="مخاطب ابلاغ",
        required=False,
        choices=[("", "بدون ابلاغ اولیه")] + list(AppraisalNotification.Recipient.choices),
    )
    notification_recipient_detail = forms.CharField(label="جزئیات مخاطب", max_length=255, required=False)
    notification_notes = forms.CharField(label="توضیحات ابلاغ", required=False, widget=forms.Textarea(attrs={"rows": 2}))
    response_number = forms.CharField(label="شماره جواب کارشناسی", max_length=120, required=False)
    response_date = JalaliDateField(label="تاریخ جواب کارشناسی", required=False)
    appraisal_date = JalaliDateField(label="تاریخ خود کارشناسی", required=False)
    amount_rial = forms.DecimalField(label="مبلغ کارشناسی (ریال)", required=False, min_value=1, decimal_places=0, max_digits=24)
    status = forms.CharField(label="وضعیت فرآیند", max_length=80, required=False, help_text="تا ایجاد Reference Data نهایی فقط وضعیت واقعی پرونده ثبت شود.")
    is_current = forms.BooleanField(label="این کارشناسی مرجع جاری فضای تجاری است", required=False)
    reference = forms.CharField(label="مرجع / شماره مرتبط", max_length=255, required=False)
    notes = forms.CharField(label="توضیحات", required=False, widget=forms.Textarea(attrs={"rows": 3}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["appraiser"].queryset = Appraiser.objects.filter(
            archived_at__isnull=True,
            collaboration_status=Appraiser.CollaborationStatus.ACTIVE,
        ).order_by("last_name", "first_name")
        self.fields["amount_rial"].widget.attrs.update({"inputmode": "numeric", "min": "1"})

    def clean(self):
        cleaned = super().clean()
        notification_fields = [
            cleaned.get("notification_number"), cleaned.get("notification_date"),
            cleaned.get("notification_recipient"), cleaned.get("notification_recipient_detail"),
        ]
        if any(notification_fields) and not cleaned.get("notification_date"):
            self.add_error("notification_date", "در صورت ثبت ابلاغ، تاریخ ابلاغ الزامی است.")
        if any(notification_fields) and not cleaned.get("notification_recipient"):
            self.add_error("notification_recipient", "در صورت ثبت ابلاغ، مخاطب ابلاغ الزامی است.")
        if cleaned.get("is_current") and (not cleaned.get("appraisal_date") or cleaned.get("amount_rial") is None):
            raise ValidationError("کارشناسی مرجع باید تاریخ خود کارشناسی و مبلغ کارشناسی داشته باشد.")
        return cleaned



class BeneficiaryAssignmentForm(forms.Form):
    beneficiary = forms.ModelChoiceField(
        label="بهره‌بردار",
        queryset=Beneficiary.objects.none(),
        empty_label="انتخاب بهره‌بردار ثبت‌شده",
    )
    start_date = JalaliDateField(label="تاریخ شروع ارتباط", required=True)
    basis = forms.CharField(
        label="مبنای ارتباط",
        max_length=120,
        required=False,
        help_text="مثال: بهره‌برداری جاری، دستور اداری یا قرارداد مرتبط",
    )
    termination_reason = forms.CharField(
        label="علت خاتمه رابطه قبلی",
        required=False,
        widget=forms.Textarea(attrs={"rows": 2}),
        help_text="فقط هنگام جایگزینی بهره‌بردار جاری الزامی است.",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["beneficiary"].queryset = Beneficiary.objects.filter(
            archived_at__isnull=True
        ).order_by("name")
