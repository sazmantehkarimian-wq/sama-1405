from django.urls import include,path
from django.contrib.auth import views as auth_views
from ui import views, action_center_views, dashboard_auction_views, auction_flow_views, auction_flow_detail_views, auction_config_views, auction_complete_views, auction_contract_views, auction_participant_views
from ui.forms import PersianAuthenticationForm
urlpatterns=[
 path('login/',auth_views.LoginView.as_view(template_name='ui/login.html',redirect_authenticated_user=True,authentication_form=PersianAuthenticationForm),name='login'),
 path('logout/',auth_views.LogoutView.as_view(),name='logout'),
 path('actions/',action_center_views.action_center,name='action-center'),
 path('dashboard/auctions/',dashboard_auction_views.auction_drilldown,name='dashboard-auction-drilldown'),
 # End-to-end auction routes are declared before legacy ui.urls so reverse/resolve use the complete flow.
 path('auctions/config/',auction_config_views.auction_configuration,name='auction-configuration'),
 path('auctions/config/organization/',auction_flow_views.organization_profile_save,name='auction-organization-profile-save'),
 path('auctions/config/templates/import/',auction_flow_views.template_pack_import,name='auction-template-pack-import'),
 path('auctions/periods/<int:period_id>/',auction_flow_detail_views.auction_period_detail,name='auction-period-detail'),
 path('auctions/periods/<int:period_id>/profile/',auction_flow_views.period_profile_save,name='auction-period-profile-save'),
 path('auctions/periods/<int:period_id>/participants/new/',auction_participant_views.participant_create,name='auction-participant-create'),
 path('auctions/participants/<int:participant_id>/edit/',auction_participant_views.participant_edit,name='auction-participant-edit'),
 path('auctions/periods/<int:period_id>/opening-sessions/new/',auction_complete_views.opening_session_create,name='auction-opening-session-create'),
 path('auctions/lots/<int:lot_id>/profile/',auction_flow_views.lot_profile_save,name='auction-lot-profile-save'),
 path('auctions/lots/<int:lot_id>/proposals/new/',auction_complete_views.proposal_create,name='auction-proposal-create'),
 path('auctions/proposals/<int:proposal_id>/edit/',auction_complete_views.proposal_edit,name='auction-proposal-edit'),
 path('auctions/lots/<int:lot_id>/winner/',auction_complete_views.winner_select,name='auction-winner-select'),
 path('auctions/lots/<int:lot_id>/contract/start/',auction_contract_views.contract_start,name='auction-contract-start'),
 path('auctions/lots/<int:lot_id>/documents/<str:document_type>/generate/',auction_contract_views.document_generate,name='auction-document-generate'),
 path('',include('ui.urls')),
]
