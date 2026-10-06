from django.urls import path
from . import views

urlpatterns = [
    path('', views.workspace, name='commission-workspace'),
    path('sessions/new/', views.session_create_page, name='commission-session-new'),
    path('sessions/create/', views.session_create, name='commission-session-create'),
    path('sessions/<int:session_id>/', views.session_detail, name='commission-session-detail'),
    path('sessions/<int:session_id>/cases/create/', views.case_create, name='commission-case-create'),
    path('cases/<int:case_id>/', views.case_detail, name='commission-case-detail'),
    path('cases/<int:case_id>/decisions/create/', views.decision_create, name='commission-decision-create'),
    path('decisions/<int:decision_id>/followups/create/', views.followup_create, name='commission-followup-create'),
    path('followups/<int:followup_id>/complete/', views.followup_complete, name='commission-followup-complete'),
]
