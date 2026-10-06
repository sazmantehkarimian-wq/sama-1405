from django.urls import path

from . import views

app_name = "masterdata"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("search/", views.search, name="search"),
    path("organization/", views.organization, name="organization"),
    path("organization/units/add/", views.unit_edit, name="unit-add"),
    path("organization/units/<int:pk>/edit/", views.unit_edit, name="unit-edit"),
    path("organization/people/add/", views.person_edit, name="person-add"),
    path("organization/people/<int:pk>/edit/", views.person_edit, name="person-edit"),
    path("organization/assignments/add/", views.assignment_edit, name="assignment-add"),
    path("organization/assignments/<int:pk>/edit/", views.assignment_edit, name="assignment-edit"),
    path("categories/", views.categories, name="categories"),
    path("categories/add/", views.category_edit, name="category-add"),
    path("categories/<int:pk>/edit/", views.category_edit, name="category-edit"),
]
