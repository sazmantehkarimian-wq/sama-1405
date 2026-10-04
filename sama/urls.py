from django.urls import include,path
from django.contrib.auth import views as auth_views
from ui import views, action_center_views, dashboard_auction_views, auction_flow_views, auction_flow_detail_views
from ui.forms import PersianAuthenticationForm
urlpatterns=[
 path('login/',auth_views.LoginView.as_view(template_name='ui/login.html',redirect_authenticated_user=True,authentication_form=PersianAuthenticationForm),name='login'),
 path('logout/',auth_views.LogoutView.as_view(),name='logout'),
 path('actions/',action_center_views.action_center,name='action-center'),
 path('dashboard/auctions/',dashboard_auction_views.auction_drilldown,name='dashboard-auction-drilldown'),
 # End-to-end auction routes are declared before legacy ui.urls so reverse/resolve use the complete flow.
 path('auctions/periods/<int:period_id>/',auction_flow_detail_views.auction_period_detail,name='auction-period-detail'),
 path('auctions/periods/<int:period_id>/profile/',auction_flow_views.period_profile_save,name='auction-period-profile-save'),
 path('auctions/lots/<int:lot_id>/profile/',auction_flow_views.lot_profile_save,name='auction-lot-profile-save'),
 path('auctions/lots/<int:lot_id>/winner/',auction_flow_views.winner_select,name='auction-winner-select'),
 path('auctions/lots/<int:lot_id>/contract/start/',auction_flow_views.contract_start,name='auction-contract-start'),
 path('auctions/lots/<int:lot_id>/documents/<str:document_type>/generate/',auction_flow_views.document_generate,name='auction-document-generate'),
 path('',include('ui.urls')),
]
