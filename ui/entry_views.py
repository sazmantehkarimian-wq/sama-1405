from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from domains.contracts.models import Beneficiary
from domains.identity.models import AuditEvent
from domains.operations.models import (
    Appraiser, AppraisalFee, ElectricityBill, ElectricityConsumptionCategory,
    UtilityBill, UtilityConnection, UtilityMeasurement, UtilityParameterRule, UtilityUnit,
)
from domains.properties.models import Center, CommercialSpace, MotherProperty, Region
from services.contracts import assign_beneficiary, create_contract
from services.electricity import (
    create_electricity_bill, electricity_bill_issues, finalize_electricity_bill,
    record_measurement, recalculate_electricity_bill, reopen_electricity_bill, update_electricity_bill,
    upsert_electricity_allocation,
)
from services.operations import (
    create_appraisal, create_appraisal_fee, create_fee_payment_batch,
    transition_appraisal_fee, update_appraisal_fee_amount,
)
from services.utilities import create_utility_bill, create_utility_connection
from ui.entry_forms import (
    AppraisalEntryForm, AppraisalFeeAmountForm, AppraisalFeeCreateForm, AppraisalFeeTransitionForm,
    AppraiserForm, BeneficiaryAssignmentForm, BeneficiaryForm,
    CenterForm, CommercialSpaceForm, ContractEntryForm, ElectricityAllocationForm, ExpertFeeBatchForm,
    ElectricityBillForm, MotherPropertyForm, RegionForm, UtilityBillForm,
    UtilityConnectionForm, UtilityMeasurementForm, UtilityParameterRuleForm, UtilityUnitForm,
)


def _ip(request):
    return request.META.get("REMOTE_ADDR")


@login_required
@transaction.atomic
def commercial_space_create(request):
    form = CommercialSpaceForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        space = form.save()
        AuditEvent.objects.create(
            actor=request.user,
            action="COMMERCIAL_SPACE_CREATE",
            entity_type="CommercialSpace",
            entity_id=space.code,
            after={
                "code": space.code,
                "name": space.name,
                "status": space.status,
                "region_id": space.region_id,
                "center_id": space.center_id,
            },
            ip_address=_ip(request),
        )
        messages.success(request, f"پرونده فضای تجاری {space.code} ایجاد شد.")
        return redirect("space-detail", code=space.code)
    return render(
        request,
        "ui/entity_form.html",
        {
            "form": form,
            "title": "ثبت فضای تجاری",
            "subtitle": "کد فضا پس از ثبت غیرقابل تغییر است.",
            "cancel_url": "space-list",
        },
    )


@login_required
@transaction.atomic
def commercial_space_edit(request, code):
    space = get_object_or_404(CommercialSpace, code=code)
    before = {
        "name": space.name,
        "status": space.status,
        "region_id": space.region_id,
        "center_id": space.center_id,
        "organizational_scope": space.organizational_scope,
        "asset_type": space.asset_type,
        "area": str(space.area) if space.area is not None else None,
        "address": space.address,
        "current_usage": space.current_usage,
        "proposed_activity": space.proposed_activity,
        "activity_group": space.activity_group,
        "previous_usage": space.previous_usage,
    }
    form = CommercialSpaceForm(request.POST or None, instance=space)
    if request.method == "POST" and form.is_valid():
        updated = form.save()
        after = {
            "name": updated.name,
            "status": updated.status,
            "region_id": updated.region_id,
            "center_id": updated.center_id,
            "organizational_scope": updated.organizational_scope,
            "asset_type": updated.asset_type,
            "area": str(updated.area) if updated.area is not None else None,
            "address": updated.address,
            "current_usage": updated.current_usage,
            "proposed_activity": updated.proposed_activity,
            "activity_group": updated.activity_group,
            "previous_usage": updated.previous_usage,
        }
        AuditEvent.objects.create(
            actor=request.user,
            action="COMMERCIAL_SPACE_UPDATE",
            entity_type="CommercialSpace",
            entity_id=updated.code,
            before=before,
            after=after,
            reason=request.POST.get("change_reason", "").strip(),
            ip_address=_ip(request),
        )
        messages.success(request, "اطلاعات پایه فضای تجاری به‌روزرسانی شد.")
        return redirect("space-detail", code=updated.code)
    return render(
        request,
        "ui/entity_form.html",
        {
            "form": form,
            "title": f"ویرایش فضای تجاری {space.code}",
            "subtitle": "کد فضا ثابت است؛ تغییر وضعیت‌های تاریخی باید از گردش وضعیت انجام شود.",
            "cancel_url": "space-detail",
            "cancel_kwargs": {"code": space.code},
            "show_change_reason": True,
        },
    )


@login_required
@transaction.atomic
def mother_property_create(request):
    form = MotherPropertyForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        item = form.save()
        AuditEvent.objects.create(
            actor=request.user,
            action="MOTHER_PROPERTY_CREATE",
            entity_type="MotherProperty",
            entity_id=item.identifier,
            after={
                "identifier": item.identifier,
                "name": item.name,
                "region_id": item.region_id,
                "center_type": item.center_type,
                "primary_usage": item.primary_usage,
                "usage_group": item.usage_group,
                "area": str(item.area) if item.area is not None else None,
            },
            ip_address=_ip(request),
        )
        messages.success(request, f"ملک مادر {item.identifier} ایجاد شد.")
        return redirect("domain-list", domain="properties")
    return render(
        request,
        "ui/entity_form.html",
        {
            "form": form,
            "title": "ثبت ملک مادر",
            "subtitle": "ملک مادر دامنه‌ای مستقل از کد فضای تجاری است.",
            "cancel_url": "domain-list",
            "cancel_kwargs": {"domain": "properties"},
        },
    )


@login_required
@transaction.atomic
def mother_property_edit(request, pk):
    item = get_object_or_404(MotherProperty, pk=pk)
    before = {
        "name": item.name,
        "region_id": item.region_id,
        "center_type": item.center_type,
        "primary_usage": item.primary_usage,
        "usage_group": item.usage_group,
        "area": str(item.area) if item.area is not None else None,
        "address": item.address,
        "notes": item.notes,
    }
    form = MotherPropertyForm(request.POST or None, instance=item)
    if request.method == "POST" and form.is_valid():
        updated = form.save()
        after = {
            "name": updated.name,
            "region_id": updated.region_id,
            "center_type": updated.center_type,
            "primary_usage": updated.primary_usage,
            "usage_group": updated.usage_group,
            "area": str(updated.area) if updated.area is not None else None,
            "address": updated.address,
            "notes": updated.notes,
        }
        AuditEvent.objects.create(
            actor=request.user,
            action="MOTHER_PROPERTY_UPDATE",
            entity_type="MotherProperty",
            entity_id=updated.identifier,
            before=before,
            after=after,
            reason=request.POST.get("change_reason", "").strip(),
            ip_address=_ip(request),
        )
        messages.success(request, "اطلاعات ملک مادر به‌روزرسانی شد.")
        return redirect("domain-list", domain="properties")
    return render(
        request,
        "ui/entity_form.html",
        {
            "form": form,
            "title": f"ویرایش ملک مادر {item.identifier}",
            "subtitle": "شناسه ملک مادر ثابت و مستقل از کد فضای تجاری است.",
            "cancel_url": "domain-list",
            "cancel_kwargs": {"domain": "properties"},
            "show_change_reason": True,
        },
    )


@login_required
@user_passes_test(lambda u: u.is_staff)
def location_settings(request):
    region_form = RegionForm(prefix="region")
    center_form = CenterForm(prefix="center")
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "region":
            region_form = RegionForm(request.POST, prefix="region")
            if region_form.is_valid():
                region = region_form.save()
                AuditEvent.objects.create(
                    actor=request.user, action="REGION_CREATE",
                    entity_type="Region", entity_id=region.code,
                    after={"code": region.code, "name": region.name}, ip_address=_ip(request),
                )
                messages.success(request, "منطقه ثبت شد.")
                return redirect("location-settings")
        elif action == "center":
            center_form = CenterForm(request.POST, prefix="center")
            if center_form.is_valid():
                center = center_form.save()
                AuditEvent.objects.create(
                    actor=request.user, action="CENTER_CREATE",
                    entity_type="Center", entity_id=str(center.pk),
                    after={"name": center.name, "region_id": center.region_id}, ip_address=_ip(request),
                )
                messages.success(request, "مرکز ثبت شد.")
                return redirect("location-settings")
    return render(
        request,
        "ui/location_settings.html",
        {
            "region_form": region_form,
            "center_form": center_form,
            "regions": Region.objects.order_by("code"),
            "centers": Center.objects.select_related("region").order_by("name"),
        },
    )



@login_required
@transaction.atomic
def beneficiary_create(request):
    form = BeneficiaryForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        beneficiary = form.save(commit=False)
        beneficiary.created_by = request.user
        beneficiary.save()
        AuditEvent.objects.create(
            actor=request.user,
            action="BENEFICIARY_CREATE",
            entity_type="Beneficiary",
            entity_id=str(beneficiary.pk),
            after={
                "code": beneficiary.sama_code,
                "kind": beneficiary.kind,
                "name": beneficiary.name,
                "identity_number": beneficiary.identity_number,
            },
            ip_address=_ip(request),
        )
        messages.success(request, f"پرونده بهره‌بردار {beneficiary.sama_code} ایجاد شد.")
        return redirect("beneficiary-detail", pk=beneficiary.pk)
    return render(
        request,
        "ui/entity_form.html",
        {
            "form": form,
            "title": "ثبت بهره‌بردار",
            "subtitle": "شخص حقیقی و حقوقی با ساختار هویتی مستقل ثبت می‌شوند. نبود شناسه هویتی مانع ثبت اولیه نیست.",
            "cancel_url": "domain-list",
            "cancel_kwargs": {"domain": "beneficiaries"},
        },
    )


@login_required
@transaction.atomic
def beneficiary_edit(request, pk):
    beneficiary = get_object_or_404(Beneficiary, pk=pk, archived_at__isnull=True)
    before = {
        "kind": beneficiary.kind,
        "name": beneficiary.name,
        "identity_number": beneficiary.identity_number,
        "mobile": beneficiary.mobile,
        "phone": beneficiary.phone,
        "address": beneficiary.address,
        "representative_name": beneficiary.representative_name,
    }
    form = BeneficiaryForm(request.POST or None, instance=beneficiary)
    if request.method == "POST" and form.is_valid():
        updated = form.save()
        after = {
            "kind": updated.kind,
            "name": updated.name,
            "identity_number": updated.identity_number,
            "mobile": updated.mobile,
            "phone": updated.phone,
            "address": updated.address,
            "representative_name": updated.representative_name,
        }
        AuditEvent.objects.create(
            actor=request.user,
            action="BENEFICIARY_UPDATE",
            entity_type="Beneficiary",
            entity_id=str(updated.pk),
            before=before,
            after=after,
            reason=request.POST.get("change_reason", "").strip(),
            ip_address=_ip(request),
        )
        messages.success(request, "اطلاعات بهره‌بردار به‌روزرسانی شد.")
        return redirect("beneficiary-detail", pk=updated.pk)
    return render(
        request,
        "ui/entity_form.html",
        {
            "form": form,
            "title": f"ویرایش بهره‌بردار {beneficiary.sama_code}",
            "subtitle": "سوابق قرارداد و ارتباط با فضا از پرونده‌های اصلی خود خوانده می‌شوند و overwrite نمی‌شوند.",
            "cancel_url": "beneficiary-detail",
            "cancel_kwargs": {"pk": beneficiary.pk},
            "show_change_reason": True,
        },
    )


@login_required
def beneficiary_detail(request, pk):
    beneficiary = get_object_or_404(Beneficiary, pk=pk, archived_at__isnull=True)
    assignments = beneficiary.space_assignments.select_related("space").order_by("-start_date", "-id")
    contracts = beneficiary.contracts.select_related("space").order_by("-start_date", "-id")
    audit = AuditEvent.objects.filter(entity_type="Beneficiary", entity_id=str(beneficiary.pk)).order_by("-created_at")[:100]
    return render(
        request,
        "ui/beneficiary_detail.html",
        {
            "beneficiary": beneficiary,
            "assignments": assignments,
            "contracts": contracts,
            "audit_events": audit,
        },
    )


@login_required
@transaction.atomic
def contract_create(request, code):
    space = get_object_or_404(CommercialSpace, code=code)
    form = ContractEntryForm(request.POST or None, space=space)
    if request.method == "POST" and form.is_valid():
        try:
            contract = create_contract(
                space=space,
                beneficiary=form.cleaned_data["beneficiary"],
                actor=request.user,
                values=form.cleaned_data,
                ip_address=_ip(request),
            )
        except Exception as exc:
            from django.core.exceptions import ValidationError
            if isinstance(exc, ValidationError):
                form.add_error(None, " ".join(exc.messages))
            else:
                raise
        else:
            messages.success(request, f"قرارداد {contract.number} ثبت شد.")
            return redirect("space-detail", code=space.code)
    return render(
        request,
        "ui/entity_form.html",
        {
            "form": form,
            "title": f"ثبت قرارداد برای فضای {space.code}",
            "subtitle": "بهره‌بردار باید قبلاً پرونده مستقل داشته باشد. سامانه بازه قراردادهای همین کد فضا را کنترل می‌کند.",
            "cancel_url": "space-detail",
            "cancel_kwargs": {"code": space.code},
            "secondary_action_url": "beneficiary-create",
            "secondary_action_label": "ثبت بهره‌بردار جدید",
        },
    )



@login_required
@transaction.atomic
def appraiser_create(request):
    form = AppraiserForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        appraiser = form.save(commit=False)
        appraiser.created_by = request.user
        appraiser.save()
        AuditEvent.objects.create(
            actor=request.user,
            action="APPRAISER_CREATE",
            entity_type="Appraiser",
            entity_id=str(appraiser.pk),
            after={
                "code": appraiser.sama_code,
                "name": appraiser.full_name,
                "national_id": appraiser.national_id,
                "license_number": appraiser.license_number,
            },
            ip_address=_ip(request),
        )
        messages.success(request, f"پرونده کارشناس {appraiser.sama_code} ایجاد شد.")
        return redirect("appraiser-detail", pk=appraiser.pk)
    return render(
        request,
        "ui/entity_form.html",
        {
            "form": form,
            "title": "ثبت کارشناس",
            "subtitle": "کنترل تکرار بر اساس کد ملی و شماره پروانه انجام می‌شود.",
            "cancel_url": "domain-list",
            "cancel_kwargs": {"domain": "appraisers"},
        },
    )


@login_required
@transaction.atomic
def appraiser_edit(request, pk):
    appraiser = get_object_or_404(Appraiser, pk=pk, archived_at__isnull=True)
    before = {
        "name": appraiser.full_name,
        "national_id": appraiser.national_id,
        "license_number": appraiser.license_number,
        "specialty": appraiser.specialty,
        "collaboration_status": appraiser.collaboration_status,
    }
    form = AppraiserForm(request.POST or None, instance=appraiser)
    if request.method == "POST" and form.is_valid():
        updated = form.save()
        after = {
            "name": updated.full_name,
            "national_id": updated.national_id,
            "license_number": updated.license_number,
            "specialty": updated.specialty,
            "collaboration_status": updated.collaboration_status,
        }
        AuditEvent.objects.create(
            actor=request.user,
            action="APPRAISER_UPDATE",
            entity_type="Appraiser",
            entity_id=str(updated.pk),
            before=before,
            after=after,
            reason=request.POST.get("change_reason", "").strip(),
            ip_address=_ip(request),
        )
        messages.success(request, "اطلاعات کارشناس به‌روزرسانی شد.")
        return redirect("appraiser-detail", pk=updated.pk)
    return render(
        request,
        "ui/entity_form.html",
        {
            "form": form,
            "title": f"ویرایش کارشناس {appraiser.sama_code}",
            "subtitle": "سوابق کارشناسی قبلی حذف یا overwrite نمی‌شوند.",
            "cancel_url": "appraiser-detail",
            "cancel_kwargs": {"pk": appraiser.pk},
            "show_change_reason": True,
        },
    )


@login_required
def appraiser_detail(request, pk):
    appraiser = get_object_or_404(Appraiser, pk=pk, archived_at__isnull=True)
    appraisals = appraiser.appraisals.select_related("space").order_by("-appraisal_date", "-id")
    audit = AuditEvent.objects.filter(entity_type="Appraiser", entity_id=str(appraiser.pk)).order_by("-created_at")[:100]
    return render(
        request,
        "ui/appraiser_detail.html",
        {
            "appraiser": appraiser,
            "appraisals": appraisals,
            "audit_events": audit,
        },
    )


@login_required
@transaction.atomic
def appraisal_create(request, code):
    space = get_object_or_404(CommercialSpace, code=code)
    form = AppraisalEntryForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        appraisal = create_appraisal(
            space=space,
            appraiser=form.cleaned_data["appraiser"],
            actor=request.user,
            values=form.cleaned_data,
            document=None,
            ip_address=_ip(request),
        )
        messages.success(request, f"کارشناسی {appraisal.sama_code} ثبت شد.")
        return redirect("space-detail", code=space.code)
    return render(
        request,
        "ui/entity_form.html",
        {
            "form": form,
            "title": f"ثبت کارشناسی برای فضای {space.code}",
            "subtitle": "تاریخ ابلاغ، تاریخ جواب و تاریخ خود کارشناسی مستقل هستند و با یکدیگر جایگزین نمی‌شوند.",
            "cancel_url": "space-detail",
            "cancel_kwargs": {"code": space.code},
            "secondary_action_url": "appraiser-create",
            "secondary_action_label": "ثبت کارشناس جدید",
        },
    )



@login_required
@transaction.atomic
def beneficiary_assign(request, code):
    space = get_object_or_404(CommercialSpace, code=code)
    form = BeneficiaryAssignmentForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        from django.core.exceptions import ValidationError
        try:
            assignment = assign_beneficiary(
                space=space,
                beneficiary=form.cleaned_data["beneficiary"],
                actor=request.user,
                start_date=form.cleaned_data["start_date"],
                basis=form.cleaned_data.get("basis", ""),
                termination_reason=form.cleaned_data.get("termination_reason", ""),
                ip_address=_ip(request),
            )
        except ValidationError as exc:
            form.add_error(None, " ".join(exc.messages))
        else:
            messages.success(request, f"بهره‌بردار {assignment.beneficiary.name} برای فضای {space.code} ثبت شد.")
            return redirect("space-detail", code=space.code)
    return render(
        request,
        "ui/entity_form.html",
        {
            "form": form,
            "title": f"ثبت / تغییر بهره‌بردار فضای {space.code}",
            "subtitle": "وجود بهره‌بردار مستقل از وجود قرارداد است؛ تغییر بهره‌بردار سابقه قبلی را حذف نمی‌کند.",
            "cancel_url": "space-detail",
            "cancel_kwargs": {"code": space.code},
            "secondary_action_url": "beneficiary-create",
            "secondary_action_label": "ثبت بهره‌بردار جدید",
        },
    )



@login_required
def electricity_dashboard(request):
    bills = ElectricityBill.objects.select_related("unit", "created_by").prefetch_related("allocations").order_by("-period_end", "-id")
    status_filter = request.GET.get("status", "").strip()
    if status_filter in ElectricityBill.Status.values:
        bills = bills.filter(status=status_filter)
    units = UtilityUnit.objects.filter(active=True).order_by("name")
    context = {
        "bills": bills[:200],
        "units": units,
        "rules": UtilityParameterRule.objects.order_by("key", "-effective_from", "-id")[:100],
        "rule_form": UtilityParameterRuleForm(),
        "bill_count": bills.count(),
        "final_count": bills.filter(status=ElectricityBill.Status.FINAL).count(),
        "review_count": bills.filter(status=ElectricityBill.Status.REVIEW_REQUIRED).count(),
        "total_amount": sum((item.amount_rial for item in bills), 0),
    }
    return render(request, "ui/electricity_dashboard.html", context)


@login_required
@user_passes_test(lambda u: u.is_staff)
@transaction.atomic
def utility_unit_create(request):
    form = UtilityUnitForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        unit = form.save(commit=False)
        unit.created_by = request.user
        unit.save()
        AuditEvent.objects.create(
            actor=request.user,
            action="UTILITY_UNIT_CREATE",
            entity_type="UtilityUnit",
            entity_id=str(unit.pk),
            after={"name": unit.name, "kind": unit.kind, "region_id": unit.region_id, "center_id": unit.center_id},
            ip_address=_ip(request),
        )
        messages.success(request, "واحد برق ثبت شد.")
        return redirect("electricity-dashboard")
    return render(
        request,
        "ui/entity_form.html",
        {
            "form": form,
            "title": "تعریف واحد برق",
            "subtitle": "واحد می‌تواند منطقه، مرکز خاص یا واحد مصوب دیگری باشد.",
            "cancel_url": "electricity-dashboard",
        },
    )


@login_required
@user_passes_test(lambda u: u.is_staff)
@transaction.atomic
def electricity_category_create(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        eui_raw = request.POST.get("eui", "").strip()
        effective_from = request.POST.get("effective_from", "").strip()
        if not name:
            messages.error(request, "نام دسته مصرف الزامی است.")
        elif ElectricityConsumptionCategory.objects.filter(name=name).exists():
            messages.error(request, "این دسته مصرف قبلاً ثبت شده است.")
        else:
            from decimal import Decimal, InvalidOperation
            try:
                eui = Decimal(eui_raw) if eui_raw else None
                if eui is not None and eui < 0:
                    raise InvalidOperation
            except InvalidOperation:
                messages.error(request, "EUI باید عدد غیرمنفی معتبر باشد.")
            else:
                category = ElectricityConsumptionCategory.objects.create(
                    name=name,
                    eui=eui,
                    effective_from=effective_from,
                    notes=request.POST.get("notes", "").strip(),
                    created_by=request.user,
                )
                AuditEvent.objects.create(
                    actor=request.user,
                    action="ELECTRICITY_CATEGORY_CREATE",
                    entity_type="ElectricityConsumptionCategory",
                    entity_id=str(category.pk),
                    after={"name": category.name, "eui": str(category.eui) if category.eui is not None else None},
                    ip_address=_ip(request),
                )
                messages.success(request, "دسته مصرف برق ثبت شد.")
    return redirect("electricity-dashboard")


@login_required
@transaction.atomic
def electricity_bill_create(request):
    form = ElectricityBillForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        from django.core.exceptions import ValidationError
        try:
            bill = create_electricity_bill(
                unit=form.cleaned_data["unit"],
                actor=request.user,
                values=form.cleaned_data,
                ip_address=_ip(request),
            )
        except ValidationError as exc:
            form.add_error(None, " ".join(exc.messages))
        else:
            messages.success(request, f"قبض برق {bill.sama_code} ثبت شد.")
            return redirect("electricity-bill-detail", bill_id=bill.pk)
    return render(
        request,
        "ui/entity_form.html",
        {
            "form": form,
            "title": "ثبت قبض برق",
            "subtitle": "مبلغ قبض و درصد سهم‌ها ساختاری ثبت می‌شوند؛ جمع سهم سازمان و بهره‌برداران باید دقیقاً ۱۰۰٪ باشد.",
            "cancel_url": "electricity-dashboard",
        },
    )


@login_required
def electricity_bill_detail(request, bill_id):
    bill = get_object_or_404(
        ElectricityBill.objects.select_related("unit", "supporting_document", "finalized_by")
        .prefetch_related("allocations__space", "allocations__measurement", "allocations__category", "snapshots"),
        pk=bill_id,
    )
    allocation_form = ElectricityAllocationForm(bill=bill, actor=request.user)
    return render(
        request,
        "ui/electricity_bill_detail.html",
        {
            "bill": bill,
            "allocation_form": allocation_form,
            "allocations": bill.allocations.select_related("space", "measurement", "category").order_by("space__code"),
            "snapshots": bill.snapshots.all(),
            "issues": electricity_bill_issues(bill),
        },
    )


@login_required
@transaction.atomic
def utility_measurement_create(request, code):
    space = get_object_or_404(CommercialSpace, code=code)
    form = UtilityMeasurementForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        from django.core.exceptions import ValidationError
        try:
            measurement = record_measurement(
                space=space,
                actor=request.user,
                values=form.cleaned_data,
                ip_address=_ip(request),
            )
        except ValidationError as exc:
            form.add_error(None, " ".join(exc.messages))
        else:
            messages.success(request, "Measurement ثبت شد و در تاریخچه باقی می‌ماند.")
            return redirect("space-detail", code=space.code)
    return render(
        request,
        "ui/entity_form.html",
        {
            "form": form,
            "title": f"ثبت Measurement برای فضای {space.code}",
            "subtitle": "داده واقعی و زیرکنتور بر داده برآوردی اولویت دارند و Measurement قبلی حذف نمی‌شود.",
            "cancel_url": "space-detail",
            "cancel_kwargs": {"code": space.code},
        },
    )


@login_required
@transaction.atomic
def electricity_allocation_save(request, bill_id):
    from django.core.exceptions import ValidationError
    bill = get_object_or_404(ElectricityBill, pk=bill_id)
    form = ElectricityAllocationForm(request.POST or None, bill=bill, actor=request.user)
    if request.method != "POST":
        return redirect("electricity-bill-detail", bill_id=bill.pk)
    if form.is_valid():
        try:
            upsert_electricity_allocation(
                bill=bill,
                space=form.cleaned_data["space"],
                actor=request.user,
                values=form.cleaned_data,
                ip_address=_ip(request),
            )
        except ValidationError as exc:
            for message in exc.messages:
                messages.error(request, message)
        else:
            messages.success(request, "فضای مشمول و پارامترهای محاسبه ثبت و قبض باز‌محاسبه شد.")
    else:
        for errors in form.errors.values():
            for error in errors:
                messages.error(request, error)
    return redirect("electricity-bill-detail", bill_id=bill.pk)


@login_required
@transaction.atomic
def electricity_recalculate(request, bill_id):
    from django.core.exceptions import ValidationError
    bill = get_object_or_404(ElectricityBill, pk=bill_id)
    try:
        recalculate_electricity_bill(bill=bill, actor=request.user, ip_address=_ip(request))
    except ValidationError as exc:
        messages.error(request, " ".join(exc.messages))
    else:
        messages.success(request, "محاسبه برق بر اساس اولویت Measurement / تجهیزات / مدل مصوب به‌روزرسانی شد.")
    return redirect("electricity-bill-detail", bill_id=bill.pk)


@login_required
@transaction.atomic
def electricity_finalize(request, bill_id):
    from django.core.exceptions import ValidationError
    bill = get_object_or_404(ElectricityBill, pk=bill_id)
    try:
        snapshot = finalize_electricity_bill(bill=bill, actor=request.user, ip_address=_ip(request))
    except ValidationError as exc:
        messages.error(request, " ".join(exc.messages))
    else:
        messages.success(request, f"محاسبه نهایی شد و Snapshot نسخه {snapshot.version} ثبت شد.")
    return redirect("electricity-bill-detail", bill_id=bill.pk)


@login_required
@user_passes_test(lambda u: u.is_staff)
@transaction.atomic
def electricity_reopen(request, bill_id):
    from django.core.exceptions import ValidationError
    bill = get_object_or_404(ElectricityBill, pk=bill_id)
    try:
        reopen_electricity_bill(
            bill=bill,
            actor=request.user,
            reason=request.POST.get("reason", ""),
            ip_address=_ip(request),
        )
    except ValidationError as exc:
        messages.error(request, " ".join(exc.messages))
    else:
        messages.success(request, "محاسبه نهایی با ثبت علت بازگشایی شد.")
    return redirect("electricity-bill-detail", bill_id=bill.pk)



@login_required
@user_passes_test(lambda u: u.is_staff)
@transaction.atomic
def electricity_bill_update(request, bill_id):
    from django.core.exceptions import ValidationError
    bill = get_object_or_404(ElectricityBill, pk=bill_id)
    if request.method == "POST":
        try:
            update_electricity_bill(
                bill=bill,
                actor=request.user,
                values=request.POST,
                reason=request.POST.get("reason", ""),
                ip_address=_ip(request),
            )
        except ValidationError as exc:
            messages.error(request, " ".join(exc.messages))
        else:
            messages.success(request, "مبلغ و درصدهای قبض با ثبت Audit اصلاح شد.")
    return redirect("electricity-bill-detail", bill_id=bill.pk)



@login_required
@user_passes_test(lambda u: u.is_staff)
@transaction.atomic
def utility_rule_create(request):
    form = UtilityParameterRuleForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        rule = form.save(commit=False)
        rule.created_by = request.user
        rule.save()
        AuditEvent.objects.create(
            actor=request.user,
            action="UTILITY_RULE_CREATE",
            entity_type="UtilityParameterRule",
            entity_id=str(rule.pk),
            after={
                "key": rule.key,
                "value_decimal": str(rule.value_decimal) if rule.value_decimal is not None else None,
                "value_text": rule.value_text,
                "effective_from": rule.effective_from,
                "effective_to": rule.effective_to,
                "active": rule.active,
            },
            ip_address=_ip(request),
        )
        messages.success(request, "Rule / Parameter جدید با تاریخ اثر ثبت شد.")
    else:
        for errors in form.errors.values():
            for error in errors:
                messages.error(request, error)
    return redirect("electricity-dashboard")



@login_required
@transaction.atomic
def utility_connection_create(request,code):
    space=get_object_or_404(CommercialSpace,code=code)
    form=UtilityConnectionForm(request.POST or None)
    if request.method=="POST" and form.is_valid():
        from django.core.exceptions import ValidationError
        try:
            connection=create_utility_connection(space=space,actor=request.user,values=form.cleaned_data,ip_address=_ip(request))
        except ValidationError as exc:
            form.add_error(None," ".join(exc.messages))
        else:
            messages.success(request,f"اشتراک {connection.get_utility_type_display()} ثبت شد.")
            return redirect("space-detail",code=space.code)
    return render(request,"ui/entity_form.html",{
        "form":form,"title":f"ثبت انشعاب برای فضای {space.code}",
        "subtitle":"آب و گاز مستقل از فرمول برق ثبت می‌شوند و سابقه حذف نمی‌شود.",
        "cancel_url":"space-detail","cancel_kwargs":{"code":space.code},
    })


@login_required
@transaction.atomic
def utility_bill_create(request,connection_id):
    connection=get_object_or_404(UtilityConnection.objects.select_related("space"),pk=connection_id)
    form=UtilityBillForm(request.POST or None,connection=connection)
    if request.method=="POST" and form.is_valid():
        from django.core.exceptions import ValidationError
        try:
            bill=create_utility_bill(connection=connection,actor=request.user,values=form.cleaned_data,document=form.cleaned_data.get("supporting_document"),ip_address=_ip(request))
        except ValidationError as exc:
            form.add_error(None," ".join(exc.messages))
        else:
            messages.success(request,f"قبض {bill.sama_code} ثبت شد.")
            return redirect("space-detail",code=connection.space.code)
    return render(request,"ui/entity_form.html",{
        "form":form,"title":f"ثبت قبض {connection.get_utility_type_display()} — {connection.account_number}",
        "subtitle":"برای آب و گاز فقط داده واقعی قبض/مصرف/Measurement ثبت می‌شود؛ فرمول برق استفاده نمی‌شود.",
        "cancel_url":"space-detail","cancel_kwargs":{"code":connection.space.code},
    })



@login_required
@transaction.atomic
def appraisal_fee_create(request,appraisal_id):
    from domains.operations.models import Appraisal
    appraisal=get_object_or_404(Appraisal.objects.select_related("space","appraiser_ref"),pk=appraisal_id)
    form=AppraisalFeeCreateForm(request.POST or None,appraisal=appraisal)
    if request.method=="POST" and form.is_valid():
        from django.core.exceptions import ValidationError
        try:
            fee=create_appraisal_fee(
                appraisal=appraisal,actor=request.user,amount=form.cleaned_data["amount_rial"],
                notes=form.cleaned_data.get("notes",""),document=form.cleaned_data.get("supporting_document"),
                follow_up_date=form.cleaned_data.get("follow_up_date",""),ip_address=_ip(request),
            )
        except ValidationError as exc:
            form.add_error(None," ".join(exc.messages))
        else:
            messages.success(request,f"پرونده حق‌الزحمه {fee.sama_code} ایجاد شد.")
            return redirect("expert-fee-dashboard")
    return render(request,"ui/entity_form.html",{
        "form":form,"title":f"ثبت حق‌الزحمه {appraisal.sama_code}",
        "subtitle":"مبلغ حق‌الزحمه مستقل از مبلغ کارشناسی و فقط به‌صورت دستی ثبت می‌شود.",
        "cancel_url":"space-detail","cancel_kwargs":{"code":appraisal.space.code},
    })


@login_required
@transaction.atomic
def appraisal_fee_transition(request,fee_id):
    fee=get_object_or_404(AppraisalFee.objects.select_related("appraisal__space"),pk=fee_id)
    form=AppraisalFeeTransitionForm(request.POST or None,fee=fee)
    if request.method=="POST" and form.is_valid():
        from django.core.exceptions import ValidationError
        try:
            transition_appraisal_fee(
                fee=fee,actor=request.user,new_status=form.cleaned_data["status"],values=form.cleaned_data,
                reason=form.cleaned_data.get("reason",""),ip_address=_ip(request),
            )
        except ValidationError as exc:
            form.add_error(None," ".join(exc.messages))
        else:
            messages.success(request,"وضعیت حق‌الزحمه ثبت شد.")
            return redirect("expert-fee-dashboard")
    return render(request,"ui/entity_form.html",{
        "form":form,"title":f"تغییر وضعیت {fee.sama_code}",
        "subtitle":f"وضعیت فعلی: {fee.get_status_display()}",
        "cancel_url":"expert-fee-dashboard",
    })


@login_required
@transaction.atomic
def appraisal_fee_amount_update(request,fee_id):
    fee=get_object_or_404(AppraisalFee.objects.select_related("appraisal__space"),pk=fee_id)
    form=AppraisalFeeAmountForm(request.POST or None,initial={"amount_rial":fee.amount_rial})
    if request.method=="POST" and form.is_valid():
        from django.core.exceptions import ValidationError
        try:
            update_appraisal_fee_amount(
                fee=fee,actor=request.user,amount=form.cleaned_data["amount_rial"],
                reason=form.cleaned_data["reason"],ip_address=_ip(request),
            )
        except ValidationError as exc:
            form.add_error(None," ".join(exc.messages))
        else:
            messages.success(request,"مبلغ حق‌الزحمه با ثبت Audit اصلاح شد.")
            return redirect("expert-fee-dashboard")
    return render(request,"ui/entity_form.html",{
        "form":form,"title":f"اصلاح مبلغ {fee.sama_code}",
        "subtitle":"پس از پرداخت یا مختومه‌شدن، اصلاح مستقیم مبلغ مجاز نیست.",
        "cancel_url":"expert-fee-dashboard",
    })


@login_required
@transaction.atomic
def expert_fee_batch_create(request):
    form=ExpertFeeBatchForm(request.POST or None)
    if request.method=="POST" and form.is_valid():
        from django.core.exceptions import ValidationError
        try:
            batch=create_fee_payment_batch(
                fees=list(form.cleaned_data["fees"]),actor=request.user,
                sent_date=form.cleaned_data["sent_date"],letter_number=form.cleaned_data["letter_number"],
                letter_date=form.cleaned_data["letter_date"],notes=form.cleaned_data.get("notes",""),
                ip_address=_ip(request),
            )
        except ValidationError as exc:
            form.add_error(None," ".join(exc.messages))
        else:
            messages.success(request,f"Batch {batch.sama_code} ایجاد و به مالی ارسال شد.")
            return redirect("expert-fee-dashboard")
    return render(request,"ui/entity_form.html",{
        "form":form,"title":"ارسال گروهی حق‌الزحمه به مالی",
        "subtitle":"فقط رکوردهای «آماده ارسال» انتخاب می‌شوند و هر رکورد فقط در یک Batch فعال عضو است.",
        "cancel_url":"expert-fee-dashboard",
    })
