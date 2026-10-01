from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from domains.identity.models import AuditEvent
from domains.properties.models import Center, CommercialSpace, MotherProperty, Region
from ui.entry_forms import CenterForm, CommercialSpaceForm, MotherPropertyForm, RegionForm


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
