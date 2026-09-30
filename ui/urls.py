from django.urls import path
from . import views
urlpatterns=[path('',views.dashboard,name='dashboard'),path('spaces/',views.space_list,name='space-list'),path('spaces/<str:code>/',views.space_detail,name='space-detail'),path('reports/spaces.xlsx',views.spaces_excel,name='spaces-excel'),path('reports/spaces.docx',views.spaces_docx,name='spaces-docx'),path('reports/spaces.pdf',views.spaces_pdf,name='spaces-pdf'),path('users/',views.user_list,name='user-list'),path('account/password/',views.password_change,name='password-change')]
