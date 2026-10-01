from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from domains.contracts.models import Beneficiary
from domains.identity.models import AuditEvent
from domains.operations.models import Appraiser
from domains.properties.models import Center, CommercialSpace, MotherProperty, Region
from services.contracts import assign_beneficiary, create_contract
from services.operations import create_appraisal
from ui.entry_forms import (
    AppraisalEntryForm, AppraiserForm, BeneficiaryAssignmentForm, BeneficiaryForm,
    CenterForm, CommercialSpaceForm, ContractEntryForm, MotherPropertyForm, RegionForm,
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
