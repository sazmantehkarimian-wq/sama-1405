from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from domains.contracts.models import Beneficiary, Contract
from domains.documents.models import Document
from domains.operations.models import (
    Appraiser, AppraisalFee, AppraisalNotification, AuctionInstruction, AuctionPeriod, CommissionDecision,
    CommissionMember, CommissionSession, ElectricityAllocation,
    ElectricityConsumptionCategory, UtilityBill, UtilityConnection, UtilityMeasurement,
    UtilityParameterRule, UtilityUnit,
)
from domains.properties.models import (
    Center, CommercialSpace, MotherProperty, MotherPropertyCorrespondence,
    MotherPropertyNote, MotherPropertyOwnership, MotherPropertyOwnershipDocument,
    MotherPropertyUsageHistory, PropertyReferenceValue, Region,
)
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
    current_status = forms.ChoiceField(label="وضعیت جاری", choices=(), required=True)
    center_type = forms.ChoiceField(label="نوع مرکز / مکان", choices=(), required=False)
    primary_usage = forms.ChoiceField(label="نوع کاربری", choices=(), required=False)
    usage_group = forms.ChoiceField(label="گروه کاربری", choices=(), required=False)
    holder_unit = forms.ChoiceField(label="واحد / مرکز در اختیارگیرنده", choices=(), required=False)
    ownership_document_status = forms.ChoiceField(label="وضعیت مستند مالکیت", choices=(), required=False)

    class Meta:
        model = MotherProperty
        fields = [
            "identifier", "name", "current_status", "region", "center_type",
            "primary_usage", "usage_group", "holder_unit", "land_area", "area",
            "address", "ownership_document_status", "owner_name", "owner_type",
            "ownership_notes", "has_utilities", "electricity_presence",
            "water_presence", "gas_presence", "other_utilities", "utility_notes", "notes",
        ]
        labels = {
            "identifier": "شناسه ملک مادر",
            "name": "نام ملک / مجموعه",
            "region": "منطقه شهرداری",
            "land_area": "مساحت عرصه (مترمربع)",
            "area": "مساحت اعیان (مترمربع)",
            "address": "نشانی",
            "owner_name": "مالک / دارنده سند",
            "owner_type": "نوع مالک",
            "ownership_notes": "توضیحات مالکیت",
            "has_utilities": "انشعابات دارد؟",
            "electricity_presence": "برق",
            "water_presence": "آب",
            "gas_presence": "گاز",
            "other_utilities": "سایر انشعابات",
            "utility_notes": "توضیح کوتاه انشعابات",
            "notes": "ملاحظات پایه",
        }
        widgets = {
            "land_area": forms.NumberInput(attrs={"min": "0", "step": "0.01", "inputmode": "decimal"}),
            "area": forms.NumberInput(attrs={"min": "0", "step": "0.01", "inputmode": "decimal"}),
            "address": forms.Textarea(attrs={"rows": 3}),
            "ownership_notes": forms.Textarea(attrs={"rows": 3}),
            "utility_notes": forms.Textarea(attrs={"rows": 2}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["region"].queryset = Region.objects.order_by("code")
        self.fields["region"].required = False
        mapping = {
            "current_status": PropertyReferenceValue.Category.STATUS,
            "center_type": PropertyReferenceValue.Category.CENTER_TYPE,
            "primary_usage": PropertyReferenceValue.Category.USAGE,
            "usage_group": PropertyReferenceValue.Category.USAGE_GROUP,
            "holder_unit": PropertyReferenceValue.Category.ORG_UNIT,
            "ownership_document_status": PropertyReferenceValue.Category.OWNERSHIP_STATUS,
        }
        for field_name, category in mapping.items():
            values = PropertyReferenceValue.objects.filter(category=category, active=True).order_by("sort_order", "value")
            choices = [("", "انتخاب کنید")] + [(item.value, item.value) for item in values]
            self.fields[field_name].choices = choices
        if self.instance and self.instance.pk:
            self.fields["identifier"].disabled = True
            self.fields["identifier"].help_text = "شناسه ملک مادر پس از ایجاد قابل تغییر نیست."

    def clean_identifier(self):
        value = normalize_persian_text(self.cleaned_data["identifier"]).upper()
        if not value:
            raise ValidationError("شناسه ملک مادر الزامی است.")
        return value


class PropertyReferenceValueForm(BaseNormalizedModelForm):
    class Meta:
        model = PropertyReferenceValue
        fields = ["category", "value", "sort_order", "active"]
        labels = {
            "category": "گروه داده مرجع",
            "value": "عنوان",
            "sort_order": "ترتیب نمایش",
            "active": "فعال",
        }

    def clean_value(self):
        value = normalize_persian_text(self.cleaned_data["value"])
        if not value:
            raise ValidationError("عنوان داده مرجع الزامی است.")
        return value


class MotherPropertyOwnershipForm(BaseNormalizedModelForm):
    start_date = JalaliDateField(label="تاریخ شروع", required=False)
    end_date = JalaliDateField(label="تاریخ پایان", required=False)

    class Meta:
        model = MotherPropertyOwnership
        fields = ["owner_name", "owner_type", "share_percent", "start_date", "end_date", "basis", "notes"]
        labels = {
            "owner_name": "نام مالک",
            "owner_type": "نوع مالک",
            "share_percent": "سهم مالکیت (%)",
            "basis": "مبنای مالکیت",
            "notes": "توضیحات",
        }
        widgets = {
            "share_percent": forms.NumberInput(attrs={"min": "0", "max": "100", "step": "0.0001", "inputmode": "decimal"}),
            "notes": forms.Textarea(attrs={"rows": 2}),
        }

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("start_date") and cleaned.get("end_date") and cleaned["start_date"] > cleaned["end_date"]:
            self.add_error("end_date", "تاریخ پایان نمی‌تواند قبل از تاریخ شروع باشد.")
        return cleaned


class MotherPropertyOwnershipDocumentForm(BaseNormalizedModelForm):
    document_date = JalaliDateField(label="تاریخ سند / مدرک", required=False)

    class Meta:
        model = MotherPropertyOwnershipDocument
        fields = [
            "document_type", "document_number", "document_date", "notary_number",
            "notary_name", "main_plate", "sub_plate", "registration_section",
            "documented_area", "documented_owner_name", "owner_type",
            "description", "document", "status",
        ]
        labels = {
            "document_type": "نوع سند / مدرک",
            "document_number": "شماره سند",
            "notary_number": "شماره دفترخانه",
            "notary_name": "نام دفترخانه",
            "main_plate": "پلاک ثبتی اصلی",
            "sub_plate": "پلاک ثبتی فرعی",
            "registration_section": "بخش ثبتی",
            "documented_area": "مساحت مندرج در سند",
            "documented_owner_name": "نام مالک مندرج در سند",
            "owner_type": "نوع مالک",
            "description": "توضیحات سند",
            "document": "فایل / مدرک بارگذاری‌شده",
            "status": "وضعیت رکورد",
        }
        widgets = {
            "documented_area": forms.NumberInput(attrs={"min": "0", "step": "0.01", "inputmode": "decimal"}),
            "description": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, property=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["document"].queryset = Document.objects.none()
        if property:
            self.fields["document"].queryset = Document.objects.filter(
                entity_type="MotherProperty", entity_id=property.identifier, archived_at__isnull=True
            ).order_by("-uploaded_at")


class MotherPropertyUsageForm(forms.Form):
    usage_status = forms.ChoiceField(label="وضعیت بهره‌برداری", choices=(), required=True)
    holder_type = forms.ChoiceField(
        label="نوع در اختیارگیرنده", required=False,
        choices=[("", "ثبت نشده"), ("REGION", "منطقه"), ("CENTER", "مرکز"), ("INSTITUTE", "مؤسسه"), ("ORG_UNIT", "واحد سازمانی"), ("OTHER", "سایر")],
    )
    holder_unit = forms.ChoiceField(label="واحد در اختیارگیرنده", choices=(), required=False)
    beneficiary_name = forms.CharField(label="بهره‌بردار فعلی", max_length=255, required=False)
    beneficiary_type = forms.ChoiceField(
        label="نوع بهره‌بردار", required=False,
        choices=[("", "ثبت نشده"), ("NATURAL", "حقیقی"), ("LEGAL", "حقوقی"), ("ORGANIZATIONAL", "سازمانی"), ("UNKNOWN", "نامشخص")],
    )
    start_date = JalaliDateField(label="تاریخ شروع", required=True)
    basis = forms.CharField(label="مبنای بهره‌برداری / واگذاری", max_length=255, required=False)
    contract_reference = forms.CharField(label="مرجع قرارداد مرتبط", max_length=255, required=False)
    document = forms.ModelChoiceField(label="مدرک مرتبط", queryset=Document.objects.none(), required=False, empty_label="بدون مدرک")
    termination_reason = forms.CharField(label="علت خاتمه سابقه جاری", required=False, widget=forms.Textarea(attrs={"rows": 2}))
    notes = forms.CharField(label="توضیحات", required=False, widget=forms.Textarea(attrs={"rows": 2}))

    def __init__(self, *args, property=None, **kwargs):
        super().__init__(*args, **kwargs)
        statuses = PropertyReferenceValue.objects.filter(
            category=PropertyReferenceValue.Category.USAGE_STATUS, active=True
        ).order_by("sort_order", "value")
        self.fields["usage_status"].choices = [("", "انتخاب کنید")] + [(item.value, item.value) for item in statuses]
        units = PropertyReferenceValue.objects.filter(
            category=PropertyReferenceValue.Category.ORG_UNIT, active=True
        ).order_by("sort_order", "value")
        self.fields["holder_unit"].choices = [("", "ثبت نشده")] + [(item.value, item.value) for item in units]
        if property:
            self.fields["document"].queryset = Document.objects.filter(
                entity_type="MotherProperty", entity_id=property.identifier, archived_at__isnull=True
            ).order_by("-uploaded_at")


class MotherPropertyCorrespondenceForm(BaseNormalizedModelForm):
    document_date = JalaliDateField(label="تاریخ", required=False)
    due_date = JalaliDateField(label="مهلت پیگیری", required=False)
    document_type = forms.ChoiceField(
        label="نوع مدرک / مکاتبه",
        choices=[
            ("INCOMING", "نامه وارده"), ("OUTGOING", "نامه صادره"), ("MINUTES", "صورتجلسه"),
            ("AGREEMENT", "توافقنامه"), ("MOU", "تفاهم‌نامه"), ("NOTIFICATION", "ابلاغ"),
            ("REPORT", "گزارش"), ("REQUEST", "درخواست"), ("RESPONSE", "پاسخ"),
            ("PERMIT", "مجوز"), ("OTHER", "سایر"),
        ],
    )

    class Meta:
        model = MotherPropertyCorrespondence
        fields = [
            "document_type", "number", "document_date", "subject", "sender",
            "recipient", "organizational_unit", "summary", "needs_follow_up",
            "responsible", "due_date", "follow_up_status", "document", "notes",
        ]
        labels = {
            "number": "شماره",
            "subject": "موضوع",
            "sender": "فرستنده",
            "recipient": "گیرنده",
            "organizational_unit": "واحد مرتبط",
            "summary": "شرح مختصر",
            "needs_follow_up": "نیاز به پیگیری",
            "responsible": "مسئول پیگیری",
            "follow_up_status": "وضعیت پیگیری",
            "document": "فایل / مدرک",
            "notes": "توضیحات",
        }
        widgets = {"summary": forms.Textarea(attrs={"rows": 2}), "notes": forms.Textarea(attrs={"rows": 2})}

    def __init__(self, *args, property=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["responsible"].queryset = get_user_model().objects.filter(is_active=True).order_by("username")
        self.fields["document"].queryset = Document.objects.none()
        if property:
            self.fields["document"].queryset = Document.objects.filter(
                entity_type="MotherProperty", entity_id=property.identifier, archived_at__isnull=True
            ).order_by("-uploaded_at")

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("needs_follow_up"):
            if not cleaned.get("responsible"):
                self.add_error("responsible", "برای مکاتبه نیازمند پیگیری، مسئول پیگیری الزامی است.")
            if not cleaned.get("due_date"):
                self.add_error("due_date", "برای مکاتبه نیازمند پیگیری، مهلت پیگیری الزامی است.")
        return cleaned


class MotherPropertyNoteForm(BaseNormalizedModelForm):
    class Meta:
        model = MotherPropertyNote
        fields = ["subject", "text", "active"]
        labels = {"subject": "موضوع", "text": "متن یادداشت", "active": "فعال / قابل نمایش"}
        widgets = {"text": forms.Textarea(attrs={"rows": 3})}


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



class UtilityUnitForm(forms.ModelForm):
    class Meta:
        model = UtilityUnit
        fields = ["name", "kind", "region", "center", "active"]
        labels = {
            "name": "نام واحد",
            "kind": "نوع واحد",
            "region": "منطقه",
            "center": "مرکز خاص",
            "active": "فعال",
        }

    def clean(self):
        cleaned = super().clean()
        kind = cleaned.get("kind")
        region = cleaned.get("region")
        center = cleaned.get("center")
        if kind == UtilityUnit.Kind.REGION and not region:
            self.add_error("region", "برای واحد نوع منطقه، انتخاب منطقه الزامی است.")
        if kind == UtilityUnit.Kind.REGION and center:
            self.add_error("center", "برای واحد نوع منطقه، مرکز نباید انتخاب شود.")
        if kind == UtilityUnit.Kind.CENTER and not center:
            self.add_error("center", "برای واحد نوع مرکز خاص، انتخاب مرکز الزامی است.")
        if region and center and center.region_id and center.region_id != region.id:
            self.add_error("center", "مرکز انتخاب‌شده متعلق به منطقه انتخاب‌شده نیست.")
        return cleaned


class ElectricityBillForm(forms.Form):
    unit = forms.ModelChoiceField(
        label="واحد",
        queryset=UtilityUnit.objects.none(),
        empty_label="انتخاب واحد",
    )
    period_start = JalaliDateField(label="شروع دوره", required=True)
    period_end = JalaliDateField(label="پایان دوره", required=True)
    bill_date = JalaliDateField(label="تاریخ قبض", required=False)
    amount_rial = forms.DecimalField(label="مبلغ قبض (ریال)", min_value=0, decimal_places=0, max_digits=24)
    beneficiary_share_percent = forms.DecimalField(label="درصد سهم بهره‌برداران", min_value=0, max_value=100, decimal_places=4, max_digits=7)
    organization_share_percent = forms.DecimalField(label="درصد سهم سازمان", min_value=0, max_value=100, decimal_places=4, max_digits=7)
    notes = forms.CharField(label="توضیحات", required=False, widget=forms.Textarea(attrs={"rows": 3}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["unit"].queryset = UtilityUnit.objects.filter(active=True).order_by("name")
        self.fields["amount_rial"].widget.attrs.update({"inputmode": "numeric", "min": "0"})
        for key in ("beneficiary_share_percent", "organization_share_percent"):
            self.fields[key].widget.attrs.update({"inputmode": "decimal", "min": "0", "max": "100", "step": "0.0001"})

    def clean(self):
        cleaned = super().clean()
        start, end = cleaned.get("period_start"), cleaned.get("period_end")
        if start and end and start > end:
            self.add_error("period_end", "پایان دوره نمی‌تواند قبل از شروع دوره باشد.")
        beneficiary = cleaned.get("beneficiary_share_percent")
        organization = cleaned.get("organization_share_percent")
        if beneficiary is not None and organization is not None and beneficiary + organization != 100:
            raise ValidationError("جمع سهم بهره‌برداران و سازمان باید دقیقاً ۱۰۰٪ باشد.")
        return cleaned


class UtilityMeasurementForm(forms.Form):
    utility_type = forms.ChoiceField(label="نوع انشعاب", choices=UtilityMeasurement.Type.choices, initial=UtilityMeasurement.Type.ELECTRICITY)
    period_start = JalaliDateField(label="شروع دوره", required=True)
    period_end = JalaliDateField(label="پایان دوره", required=True)
    consumption = forms.DecimalField(label="مقدار مصرف", min_value=0, decimal_places=3, max_digits=20)
    reading_date = JalaliDateField(label="تاریخ قرائت", required=True)
    meter_number = forms.CharField(label="شماره کنتور", max_length=120, required=False)
    measurement_unit = forms.CharField(label="واحد اندازه‌گیری", max_length=40, initial="kWh")
    source = forms.CharField(label="منبع ثبت", max_length=120, required=False)
    is_submeter = forms.BooleanField(label="زیرکنتور", required=False)
    is_valid = forms.BooleanField(label="Measurement معتبر است", required=False, initial=True)
    notes = forms.CharField(label="توضیحات", required=False, widget=forms.Textarea(attrs={"rows": 3}))

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("period_start") and cleaned.get("period_end") and cleaned["period_start"] > cleaned["period_end"]:
            self.add_error("period_end", "پایان دوره نمی‌تواند قبل از شروع دوره باشد.")
        return cleaned


class ElectricityAllocationForm(forms.Form):
    space = forms.ModelChoiceField(
        label="فضای تجاری",
        queryset=CommercialSpace.objects.none(),
        empty_label="انتخاب کد فضا",
    )
    eligible = forms.BooleanField(label="مشمول قبض", required=False, initial=True)
    category = forms.ModelChoiceField(
        label="دسته مصرف",
        queryset=ElectricityConsumptionCategory.objects.none(),
        required=False,
        empty_label="ثبت نشده",
    )
    effective_area = forms.DecimalField(label="متراژ مؤثر", required=False, min_value=0, decimal_places=2, max_digits=16)
    eui = forms.DecimalField(label="EUI", required=False, min_value=0, decimal_places=6, max_digits=16)
    operational_factor = forms.DecimalField(label="ضریب بهره‌برداری", required=False, min_value=0, decimal_places=6, max_digits=12)
    special_consumption = forms.DecimalField(label="مصرف ویژه / تجهیزات", required=False, min_value=0, decimal_places=3, max_digits=20)
    measurement = forms.ModelChoiceField(
        label="Measurement معتبر",
        queryset=UtilityMeasurement.objects.none(),
        required=False,
        empty_label="بدون Measurement",
    )
    manual_override_percent = forms.DecimalField(
        label="درصد Override دستی",
        required=False,
        min_value=0,
        max_value=100,
        decimal_places=4,
        max_digits=7,
        help_text="خالی یعنی Override وجود ندارد؛ صفر یک مقدار معتبر است.",
    )
    override_reason = forms.CharField(label="علت Override", required=False, widget=forms.Textarea(attrs={"rows": 2}))
    notes = forms.CharField(label="توضیحات", required=False, widget=forms.Textarea(attrs={"rows": 2}))

    def __init__(self, *args, bill=None, actor=None, **kwargs):
        self.bill = bill
        self.actor = actor
        super().__init__(*args, **kwargs)
        self.fields["space"].queryset = CommercialSpace.objects.order_by("code")
        self.fields["category"].queryset = ElectricityConsumptionCategory.objects.filter(active=True).order_by("name")
        measurements = UtilityMeasurement.objects.filter(utility_type=UtilityMeasurement.Type.ELECTRICITY, is_valid=True)
        if bill:
            measurements = measurements.filter(period_start__lte=bill.period_end, period_end__gte=bill.period_start)
        self.fields["measurement"].queryset = measurements.select_related("space").order_by("-reading_date", "-id")
        if actor is not None and not actor.is_staff:
            self.fields.pop("manual_override_percent", None)
            self.fields.pop("override_reason", None)

    def clean(self):
        cleaned = super().clean()
        measurement = cleaned.get("measurement")
        space = cleaned.get("space")
        if measurement and space and measurement.space_id != space.pk:
            self.add_error("measurement", "Measurement باید متعلق به همان کد فضا باشد.")
        override = cleaned.get("manual_override_percent")
        if override is not None and not cleaned.get("override_reason"):
            self.add_error("override_reason", "برای Override دستی، علت الزامی است.")
        return cleaned



class UtilityParameterRuleForm(forms.ModelForm):
    effective_from = JalaliDateField(label="تاریخ اثر", required=True)
    effective_to = JalaliDateField(label="پایان اعتبار", required=False)

    class Meta:
        model = UtilityParameterRule
        fields = [
            "key", "label", "value_decimal", "value_text", "unit",
            "effective_from", "effective_to", "active", "notes",
        ]
        labels = {
            "key": "کلید Rule / Parameter",
            "label": "عنوان",
            "value_decimal": "مقدار عددی",
            "value_text": "مقدار متنی",
            "unit": "واحد",
            "active": "فعال",
            "notes": "توضیحات",
        }
        widgets = {"notes": forms.Textarea(attrs={"rows": 2})}

    def clean(self):
        cleaned = super().clean()
        numeric = cleaned.get("value_decimal")
        text_value = (cleaned.get("value_text") or "").strip()
        if numeric is None and not text_value:
            raise ValidationError("حداقل یکی از مقدار عددی یا متنی باید ثبت شود.")
        if numeric is not None and text_value:
            raise ValidationError("برای هر Rule فقط یکی از مقدار عددی یا متنی را ثبت کنید.")
        if cleaned.get("effective_from") and cleaned.get("effective_to") and cleaned["effective_from"] > cleaned["effective_to"]:
            self.add_error("effective_to", "پایان اعتبار نمی‌تواند قبل از تاریخ اثر باشد.")
        return cleaned



class UtilityConnectionForm(forms.Form):
    utility_type=forms.ChoiceField(label="نوع انشعاب",choices=UtilityConnection.Type.choices)
    account_number=forms.CharField(label="شماره اشتراک",max_length=120)
    meter_number=forms.CharField(label="شماره کنتور",max_length=120,required=False)
    provider=forms.CharField(label="شرکت / تأمین‌کننده",max_length=255,required=False)
    status=forms.ChoiceField(label="وضعیت",choices=UtilityConnection.Status.choices,initial=UtilityConnection.Status.ACTIVE)
    notes=forms.CharField(label="توضیحات",required=False,widget=forms.Textarea(attrs={"rows":3}))


class UtilityBillForm(forms.Form):
    period_start=JalaliDateField(label="شروع دوره",required=True)
    period_end=JalaliDateField(label="پایان دوره",required=True)
    bill_date=JalaliDateField(label="تاریخ قبض",required=False)
    amount_rial=forms.DecimalField(label="مبلغ قبض (ریال)",min_value=0,decimal_places=0,max_digits=24)
    consumption=forms.DecimalField(label="مصرف",required=False,min_value=0,decimal_places=3,max_digits=20)
    measurement=forms.ModelChoiceField(label="Measurement مرتبط",queryset=UtilityMeasurement.objects.none(),required=False,empty_label="بدون Measurement")
    supporting_document=forms.ModelChoiceField(label="سند قبض",queryset=Document.objects.none(),required=False,empty_label="بدون سند")
    payment_status=forms.ChoiceField(label="وضعیت پرداخت",choices=UtilityBill.PaymentStatus.choices,initial=UtilityBill.PaymentStatus.UNKNOWN)
    payment_date=JalaliDateField(label="تاریخ پرداخت",required=False)
    notes=forms.CharField(label="توضیحات",required=False,widget=forms.Textarea(attrs={"rows":3}))

    def __init__(self,*args,connection=None,**kwargs):
        self.connection=connection
        super().__init__(*args,**kwargs)
        qs=UtilityMeasurement.objects.none()
        if connection:
            qs=UtilityMeasurement.objects.filter(
                space=connection.space,utility_type=connection.utility_type,is_valid=True
            ).order_by("-reading_date","-id")
        self.fields["measurement"].queryset=qs
        docs=Document.objects.none()
        if connection:
            docs=Document.objects.filter(entity_type="CommercialSpace",entity_id=connection.space.code,archived_at__isnull=True).order_by("-uploaded_at")
        self.fields["supporting_document"].queryset=docs
        self.fields["amount_rial"].widget.attrs.update({"inputmode":"numeric","min":"0"})

    def clean(self):
        cleaned=super().clean()
        start,end=cleaned.get("period_start"),cleaned.get("period_end")
        if start and end and start>end:self.add_error("period_end","پایان دوره نمی‌تواند قبل از شروع دوره باشد.")
        if cleaned.get("payment_status")==UtilityBill.PaymentStatus.PAID and not cleaned.get("payment_date"):
            self.add_error("payment_date","برای قبض پرداخت‌شده، تاریخ پرداخت الزامی است.")
        return cleaned



class AppraisalFeeCreateForm(forms.Form):
    amount_rial=forms.DecimalField(label="مبلغ حق‌الزحمه (ریال)",min_value=1,decimal_places=0,max_digits=24)
    follow_up_date=JalaliDateField(label="تاریخ پیگیری",required=False)
    supporting_document=forms.ModelChoiceField(label="پیوست",queryset=Document.objects.none(),required=False,empty_label="بدون پیوست")
    notes=forms.CharField(label="توضیحات",required=False,widget=forms.Textarea(attrs={"rows":3}))

    def __init__(self,*args,appraisal=None,**kwargs):
        super().__init__(*args,**kwargs)
        self.appraisal=appraisal
        docs=Document.objects.none()
        if appraisal:
            docs=Document.objects.filter(entity_type="CommercialSpace",entity_id=appraisal.space.code,archived_at__isnull=True).order_by("-uploaded_at")
        self.fields["supporting_document"].queryset=docs
        self.fields["amount_rial"].widget.attrs.update({"inputmode":"numeric","min":"1"})


class AppraisalFeeTransitionForm(forms.Form):
    status=forms.ChoiceField(label="وضعیت جدید",choices=AppraisalFee.Status.choices)
    sent_to_finance_date=JalaliDateField(label="تاریخ ارسال به مالی",required=False)
    letter_number=forms.CharField(label="شماره نامه / گردش",max_length=120,required=False)
    letter_date=JalaliDateField(label="تاریخ نامه / گردش",required=False)
    payment_date=JalaliDateField(label="تاریخ پرداخت",required=False)
    paid_amount_rial=forms.DecimalField(label="مبلغ پرداخت‌شده (ریال)",required=False,min_value=0,decimal_places=0,max_digits=24)
    payment_reference=forms.CharField(label="مرجع پرداخت",max_length=255,required=False)
    reason=forms.CharField(label="علت / توضیح",required=False,widget=forms.Textarea(attrs={"rows":2}))

    def __init__(self,*args,fee=None,**kwargs):
        self.fee=fee
        super().__init__(*args,**kwargs)
        self.fields["paid_amount_rial"].widget.attrs.update({"inputmode":"numeric","min":"0"})


class AppraisalFeeAmountForm(forms.Form):
    amount_rial=forms.DecimalField(label="مبلغ جدید حق‌الزحمه (ریال)",min_value=1,decimal_places=0,max_digits=24)
    reason=forms.CharField(label="علت اصلاح",widget=forms.Textarea(attrs={"rows":2}))


class ExpertFeeBatchForm(forms.Form):
    fees=forms.ModelMultipleChoiceField(
        label="حق‌الزحمه‌های آماده ارسال",
        queryset=AppraisalFee.objects.none(),
        widget=forms.SelectMultiple(attrs={"size":10}),
    )
    sent_date=JalaliDateField(label="تاریخ ارسال",required=True)
    letter_number=forms.CharField(label="شماره نامه / گردش",max_length=120)
    letter_date=JalaliDateField(label="تاریخ نامه / گردش",required=True)
    notes=forms.CharField(label="توضیحات",required=False,widget=forms.Textarea(attrs={"rows":2}))

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.fields["fees"].queryset=AppraisalFee.objects.filter(
            status=AppraisalFee.Status.READY_TO_SEND
        ).select_related("appraisal__space","appraisal__appraiser_ref").order_by("appraisal__space__code")



class CommissionMemberForm(BaseNormalizedModelForm):
    class Meta:
        model = CommissionMember
        fields = ["name","position","role","sign_order","start_date","end_date","status","notes"]
        labels = {
            "name":"نام عضو","position":"سمت","role":"نقش در کمیسیون","sign_order":"ترتیب امضا",
            "start_date":"تاریخ شروع","end_date":"تاریخ پایان","status":"وضعیت","notes":"توضیحات",
        }
        widgets={"notes":forms.Textarea(attrs={"rows":2})}


class CommissionSessionForm(forms.Form):
    number=forms.CharField(label="شماره جلسه",max_length=120,required=False)
    session_date=JalaliDateField(label="تاریخ جلسه",required=True)
    session_time=forms.CharField(label="ساعت جلسه",max_length=5,required=False,widget=forms.TextInput(attrs={"placeholder":"09:30","dir":"ltr"}))
    location=forms.CharField(label="محل جلسه",max_length=255,required=False)
    title=forms.CharField(label="عنوان جلسه",max_length=255,required=True)
    description=forms.CharField(label="شرح کلی",required=False,widget=forms.Textarea(attrs={"rows":3}))
    status=forms.ChoiceField(label="وضعیت جلسه",choices=CommissionSession.Status.choices,initial=CommissionSession.Status.DRAFT)
    members=forms.ModelMultipleChoiceField(label="اعضای جلسه",queryset=CommissionMember.objects.none(),required=False,widget=forms.CheckboxSelectMultiple)
    notes=forms.CharField(label="ملاحظات",required=False,widget=forms.Textarea(attrs={"rows":2}))
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.fields["members"].queryset=CommissionMember.objects.filter(status=CommissionMember.Status.ACTIVE).order_by("sign_order","name")

    def clean_session_time(self):
        value=self.cleaned_data.get("session_time","").strip()
        if not value:return ""
        import re
        if not re.fullmatch(r"(?:[01]\d|2[0-3]):[0-5]\d",value):
            raise ValidationError("ساعت جلسه باید به شکل HH:MM باشد.")
        return value


class CommissionCaseForm(forms.Form):
    title=forms.CharField(label="عنوان موضوع",max_length=255)
    description=forms.CharField(label="شرح موضوع",required=False,widget=forms.Textarea(attrs={"rows":3}))
    reason=forms.CharField(label="علت طرح در کمیسیون",required=False,widget=forms.Textarea(attrs={"rows":2}))
    case_type=forms.CharField(label="نوع موضوع",max_length=120,required=False)
    referral_reference=forms.CharField(label="مرجع ارجاع",max_length=255,required=False)
    responsible=forms.ModelChoiceField(label="مسئول پیگیری",queryset=get_user_model().objects.none(),required=False,empty_label="بدون مسئول فعلی")
    follow_up_due_date=JalaliDateField(label="مهلت پیگیری",required=False)
    spaces=forms.ModelMultipleChoiceField(label="فضاهای مرتبط",queryset=CommercialSpace.objects.none(),required=False)
    contracts=forms.ModelMultipleChoiceField(label="قراردادهای مرتبط",queryset=Contract.objects.none(),required=False)
    beneficiaries=forms.ModelMultipleChoiceField(label="بهره‌برداران مرتبط",queryset=Beneficiary.objects.none(),required=False)
    auction_periods=forms.ModelMultipleChoiceField(label="دوره‌های مزایده مرتبط",queryset=AuctionPeriod.objects.none(),required=False)
    notes=forms.CharField(label="ملاحظات",required=False,widget=forms.Textarea(attrs={"rows":2}))
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.fields["responsible"].queryset=get_user_model().objects.filter(is_active=True).order_by("username")
        self.fields["spaces"].queryset=CommercialSpace.objects.order_by("code")
        self.fields["contracts"].queryset=Contract.objects.select_related("space","beneficiary").order_by("-start_date","-pk")
        self.fields["beneficiaries"].queryset=Beneficiary.objects.filter(archived_at__isnull=True).order_by("name")
        self.fields["auction_periods"].queryset=AuctionPeriod.objects.order_by("-id")


class CommissionDecisionForm(forms.Form):
    identity=forms.CharField(label="شماره / شناسه تصمیم",max_length=120,required=False)
    decision_date=JalaliDateField(label="تاریخ تصمیم",required=True)
    decision_type=forms.CharField(label="نوع تصمیم / مصوبه",max_length=120,required=False)
    decision=forms.CharField(label="متن رسمی تصمیم",widget=forms.Textarea(attrs={"rows":4}),required=True)
    result=forms.CharField(label="نتیجه",max_length=255,required=False)
    responsible=forms.ModelChoiceField(label="مسئول اجرا / پیگیری",queryset=get_user_model().objects.none(),required=False,empty_label="بدون مسئول")
    due_date=JalaliDateField(label="مهلت اجرا",required=False)
    execution_status=forms.ChoiceField(label="وضعیت اجرا",choices=CommissionDecision.ExecutionStatus.choices)
    subsequent_action=forms.CharField(label="اقدام بعدی",required=False,widget=forms.Textarea(attrs={"rows":2}))
    document=forms.ModelChoiceField(label="سند مرتبط",queryset=Document.objects.none(),required=False,empty_label="بدون سند")
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.fields["responsible"].queryset=get_user_model().objects.filter(is_active=True).order_by("username")
        self.fields["document"].queryset=Document.objects.filter(archived_at__isnull=True).order_by("-uploaded_at")[:500]


class CommissionFollowUpForm(forms.Form):
    required_action=forms.CharField(label="اقدام موردنیاز",widget=forms.Textarea(attrs={"rows":2}))
    responsible=forms.ModelChoiceField(label="مسئول پیگیری",queryset=get_user_model().objects.none(),required=False,empty_label="بدون مسئول")
    responsible_unit=forms.CharField(label="واحد مسئول",max_length=255,required=False)
    referred_date=JalaliDateField(label="تاریخ ارجاع",required=False)
    due_date=JalaliDateField(label="مهلت",required=False)
    status=forms.ChoiceField(label="وضعیت",choices=CommissionDecision.ExecutionStatus.choices)
    completed_date=JalaliDateField(label="تاریخ انجام",required=False)
    result=forms.CharField(label="نتیجه اقدام",required=False,widget=forms.Textarea(attrs={"rows":2}))
    notes=forms.CharField(label="توضیحات",required=False,widget=forms.Textarea(attrs={"rows":2}))
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.fields["responsible"].queryset=get_user_model().objects.filter(is_active=True).order_by("username")


class CommissionFollowUpTransitionForm(forms.Form):
    status=forms.ChoiceField(label="وضعیت جدید",choices=CommissionDecision.ExecutionStatus.choices)
    completed_date=JalaliDateField(label="تاریخ انجام",required=False)
    result=forms.CharField(label="نتیجه اقدام",required=False,widget=forms.Textarea(attrs={"rows":2}))
    note=forms.CharField(label="توضیح تغییر",required=False,widget=forms.Textarea(attrs={"rows":2}))



class AuctionInstructionForm(forms.Form):
    space=forms.ModelChoiceField(label="فضای تجاری",queryset=CommercialSpace.objects.none())
    source=forms.ChoiceField(label="منبع دستور",choices=AuctionInstruction.Source.choices)
    direction=forms.ChoiceField(label="جهت اثر",choices=AuctionInstruction.Direction.choices)
    reason=forms.CharField(label="علت",widget=forms.Textarea(attrs={"rows":2}))
    reference=forms.CharField(label="مرجع / شماره مستند",max_length=255)
    effective_from=JalaliDateField(label="شروع اثر",required=True)
    effective_to=JalaliDateField(label="پایان اثر",required=False)
    commission_decision=forms.ModelChoiceField(
        label="تصمیم کمیسیون مرتبط",queryset=CommissionDecision.objects.none(),required=False,
        empty_label="بدون تصمیم کمیسیون",
    )
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.fields["space"].queryset=CommercialSpace.objects.order_by("code")
        self.fields["commission_decision"].queryset=CommissionDecision.objects.filter(case__isnull=False).order_by("-decision_date","-pk")

    def clean(self):
        cleaned=super().clean()
        if cleaned.get("source")==AuctionInstruction.Source.COMMISSION and not cleaned.get("commission_decision"):
            self.add_error("commission_decision","برای دستور کمیسیون، انتخاب تصمیم کمیسیون الزامی است.")
        return cleaned
