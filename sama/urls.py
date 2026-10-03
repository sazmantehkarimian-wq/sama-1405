from django.urls import include,path
from django.contrib.auth import views as auth_views
from ui import views, action_center_views, dashboard_auction_views
from ui.forms import PersianAuthenticationForm
urlpatterns=[
 path('login/',auth_views.LoginView.as_view(template_name='ui/login.html',redirect_authenticated_user=True,authentication_form=PersianAuthenticationForm),name='login'),
 path('logout/',auth_views.LogoutView.as_view(),name='logout'),
 path('actions/',action_center_views.action_center,name='action-center'),
 path('dashboard/auctions/',dashboard_auction_views.auction_drilldown,name='dashboard-auction-drilldown'),
 path('',include('ui.urls')),
]
