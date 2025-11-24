# assets/urls.py
from django.urls import path
from . import views

app_name = 'assets'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('room-assets/', views.room_assets_list, name='room_assets_list'),
    path('room-assets/<int:room_id>/', views.room_assets_list, name='room_assets_detail'),
    path('audits/', views.monthly_audits, name='monthly_audits'),
    path('audits/<int:audit_id>/', views.audit_detail, name='audit_detail'),
]