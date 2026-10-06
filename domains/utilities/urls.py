from django.urls import path

from . import views

app_name = "utilities"
urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("accounts/new/", views.account_create, name="account-create"),
    path("accounts/<int:pk>/", views.account_detail, name="account-detail"),
    path("accounts/<int:pk>/edit/", views.account_edit, name="account-edit"),
    path("accounts/<int:account_id>/profiles/new/", views.profile_create, name="profile-create"),
    path("accounts/<int:pk>/policy/", views.policy_edit, name="policy-edit"),
    path("profiles/<int:pk>/edit/", views.profile_edit, name="profile-edit"),
    path("accounts/<int:account_id>/bills/new/", views.bill_create, name="bill-create"),
    path("bills/<int:pk>/", views.bill_detail, name="bill-detail"),
    path("bills/<int:pk>/calculate/", views.bill_calculate, name="bill-calculate"),
    path("bills/<int:bill_id>/readings/new/", views.reading_create, name="reading-create"),
    path("bills/<int:bill_id>/payments/new/", views.payment_create, name="payment-create"),
    path("bills/<int:pk>/xlsx/", views.bill_xlsx, name="bill-xlsx"),
]
