from django import forms

from .models import OrganizationPerson, OrganizationUnit, PositionAssignment, ReferenceCategory


class PersianModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")


class OrganizationUnitForm(PersianModelForm):
    class Meta:
        model = OrganizationUnit
        fields = ["code", "name", "unit_type", "parent", "region", "center", "phone", "extension", "address", "notes", "is_active"]
        labels = {
            "code": "کد واحد",
            "name": "نام واحد",
            "unit_type": "نوع واحد",
            "parent": "واحد بالادست",
            "region": "منطقه مرتبط",
            "center": "مرکز مرتبط",
            "phone": "تلفن",
            "extension": "داخلی",
            "address": "نشانی",
            "notes": "توضیحات",
            "is_active": "فعال",
        }


class OrganizationPersonForm(PersianModelForm):
    class Meta:
        model = OrganizationPerson
        fields = ["full_name", "mobile", "phone", "extension", "email", "notes", "is_active"]
        labels = {
            "full_name": "نام و نام خانوادگی",
            "mobile": "تلفن همراه",
            "phone": "تلفن",
            "extension": "داخلی",
            "email": "ایمیل",
            "notes": "توضیحات",
            "is_active": "فعال",
        }


class PositionAssignmentForm(PersianModelForm):
    class Meta:
        model = PositionAssignment
        fields = ["person", "unit", "title", "start_date", "end_date", "is_current", "notes"]
        labels = {
            "person": "شخص",
            "unit": "واحد سازمانی",
            "title": "سمت",
            "start_date": "تاریخ شروع",
            "end_date": "تاریخ پایان",
            "is_current": "سمت فعلی",
            "notes": "توضیحات",
        }


class ReferenceCategoryForm(PersianModelForm):
    class Meta:
        model = ReferenceCategory
        fields = ["kind", "code", "name", "aliases", "sort_order", "is_active"]
        labels = {
            "kind": "گروه مرجع",
            "code": "کد",
            "name": "عنوان",
            "aliases": "نام‌های معادل",
            "sort_order": "ترتیب",
            "is_active": "فعال",
        }
        widgets = {"aliases": forms.Textarea(attrs={"rows": 2})}
