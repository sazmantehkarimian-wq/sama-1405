from django import forms

from .models import (
    UtilityAccount, UtilityAllocationPolicy, UtilityBill, UtilityMeterReading,
    UtilityPayment, UtilitySpaceProfile,
)


class PolicyForm(forms.ModelForm):
    class Meta:
        model = UtilityAllocationPolicy
        fields = ["beneficiary_percent", "organization_percent", "season_factor", "approved_reference", "notes"]
        labels = {
            "beneficiary_percent": "سهم بهره‌بردار (%)",
            "organization_percent": "سهم سازمان (%)",
            "season_factor": "ضریب فصل",
            "approved_reference": "مرجع مصوبه / تأیید",
            "notes": "توضیحات",
        }


class SpaceProfileForm(forms.ModelForm):
    class Meta:
        model = UtilitySpaceProfile
        fields = [
            "included", "consumption_category", "special_model", "area_override", "eui",
            "hours_factor", "category_factor", "row_factor", "special_consumption",
            "manual_share_percent", "manual_share_locked", "notes",
        ]


class BillForm(forms.ModelForm):
    class Meta:
        model = UtilityBill
        fields = ["period_start", "period_end", "bill_date", "due_date", "total_consumption", "amount_rial", "attachment", "notes"]


class AccountForm(forms.ModelForm):
    class Meta:
        model = UtilityAccount
        fields = [
            "utility_type", "title", "account_number", "bill_identifier", "payment_identifier",
            "meter_number", "ownership", "status", "region", "center", "mother_property",
            "dedicated_space", "technical_capacity", "service_address", "notes",
        ]


class ProfileCreateForm(forms.ModelForm):
    class Meta:
        model = UtilitySpaceProfile
        fields = [
            "space", "included", "consumption_category", "special_model", "area_override",
            "eui", "hours_factor", "category_factor", "row_factor", "special_consumption",
            "manual_share_percent", "manual_share_locked", "notes",
        ]


class MeterReadingForm(forms.ModelForm):
    class Meta:
        model = UtilityMeterReading
        fields = ["profile", "measured_consumption", "reading_date", "meter_number", "is_valid", "source_note"]

    def __init__(self, *args, bill=None, **kwargs):
        super().__init__(*args, **kwargs)
        if bill is not None:
            self.fields["profile"].queryset = bill.account.space_profiles.select_related("space").all()


class PaymentForm(forms.ModelForm):
    class Meta:
        model = UtilityPayment
        fields = ["allocation", "payer", "amount_rial", "payment_date", "reference", "attachment", "notes"]

    def __init__(self, *args, bill=None, **kwargs):
        super().__init__(*args, **kwargs)
        if bill is not None:
            self.fields["allocation"].queryset = bill.allocations.select_related("profile__space").all()
            self.fields["allocation"].required = False
