from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from domains.properties.models import Center, CommercialSpace, MotherProperty, Region

from .forms import OrganizationPersonForm, OrganizationUnitForm, PositionAssignmentForm, ReferenceCategoryForm
from .models import OrganizationPerson, OrganizationUnit, PositionAssignment, ReferenceCategory
from .selectors import search_mother_properties, search_spaces


@login_required
def dashboard(request):
    context = {
        "mother_count": MotherProperty.objects.count(),
        "space_count": CommercialSpace.objects.count(),
        "active_count": CommercialSpace.objects.filter(status=CommercialSpace.Status.ACTIVE).count(),
        "out_count": CommercialSpace.objects.filter(status=CommercialSpace.Status.OUT_OF_CYCLE).count(),
        "region_count": Region.objects.count(),
        "center_count": Center.objects.count(),
        "special_center_count": Center.objects.filter(is_special=True).count(),
        "current_assignment_count": PositionAssignment.objects.filter(is_current=True).count(),
    }
    return render(request, "masterdata/dashboard.html", context)


@login_required
def search(request):
    spaces = search_spaces(request.GET)
    mothers = search_mother_properties(request.GET)
    context = {
        "spaces": spaces[:1000],
        "mothers": mothers[:1000],
        "space_total": spaces.count(),
        "mother_total": mothers.count(),
        "regions": Region.objects.order_by("name"),
        "centers": Center.objects.select_related("region").order_by("region__name", "name"),
        "statuses": CommercialSpace.Status.choices,
    }
    return render(request, "masterdata/search.html", context)


@login_required
def organization(request):
    return render(
        request,
        "masterdata/organization.html",
        {
            "units": OrganizationUnit.objects.select_related("parent", "region", "center").all(),
            "people": OrganizationPerson.objects.all(),
            "assignments": PositionAssignment.objects.select_related("person", "unit").all(),
        },
    )


@login_required
def unit_edit(request, pk=None):
    instance = get_object_or_404(OrganizationUnit, pk=pk) if pk else None
    form = OrganizationUnitForm(request.POST or None, instance=instance)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "اطلاعات واحد سازمانی ذخیره شد.")
        return redirect("masterdata:organization")
    return render(request, "masterdata/edit.html", {"form": form, "title": "ویرایش واحد سازمانی" if instance else "افزودن واحد سازمانی"})


@login_required
def person_edit(request, pk=None):
    instance = get_object_or_404(OrganizationPerson, pk=pk) if pk else None
    form = OrganizationPersonForm(request.POST or None, instance=instance)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "اطلاعات شخص ذخیره شد.")
        return redirect("masterdata:organization")
    return render(request, "masterdata/edit.html", {"form": form, "title": "ویرایش اطلاعات شخص" if instance else "افزودن شخص"})


@login_required
def assignment_edit(request, pk=None):
    instance = get_object_or_404(PositionAssignment, pk=pk) if pk else None
    form = PositionAssignmentForm(request.POST or None, instance=instance)
    if request.method == "POST" and form.is_valid():
        assignment = form.save()
        if assignment.is_current:
            PositionAssignment.objects.filter(person=assignment.person, is_current=True).exclude(pk=assignment.pk).update(is_current=False)
        messages.success(request, "سمت و انتصاب سازمانی ذخیره شد.")
        return redirect("masterdata:organization")
    return render(request, "masterdata/edit.html", {"form": form, "title": "ویرایش سمت/انتصاب" if instance else "افزودن سمت/انتصاب"})


@login_required
def categories(request):
    return render(request, "masterdata/categories.html", {"categories": ReferenceCategory.objects.all()})


@login_required
def category_edit(request, pk=None):
    instance = get_object_or_404(ReferenceCategory, pk=pk) if pk else None
    form = ReferenceCategoryForm(request.POST or None, instance=instance)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "دسته‌بندی مرجع ذخیره شد.")
        return redirect("masterdata:categories")
    return render(request, "masterdata/edit.html", {"form": form, "title": "ویرایش دسته‌بندی" if instance else "افزودن دسته‌بندی"})
