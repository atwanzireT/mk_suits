# assets/urls.py
from django.urls import path
from . import views

app_name = 'assets'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    
    # Room Assets
    path('room-assets/', views.room_assets_list, name='room_assets_list'),
    path('room-assets/<int:room_id>/', views.room_assets_list, name='room_assets_detail'),
    path('add-asset/', views.add_room_asset, name='add_room_asset'),
    path('add-asset/<int:room_id>/', views.add_room_asset, name='add_room_asset_to_room'),
    path('edit-asset/<int:room_asset_id>/', views.edit_room_asset, name='edit_room_asset'),
    path('delete-asset/<int:room_asset_id>/', views.delete_room_asset, name='delete_room_asset'),
    
    # Maintenance
    path('maintenance/', views.maintenance_list, name='maintenance_list'),
    path('log-maintenance/', views.asset_maintenance, name='asset_maintenance'),
    path('log-maintenance/<int:room_asset_id>/', views.asset_maintenance, name='asset_maintenance_for_asset'),
    
    # Audits
    path('audits/', views.monthly_audits, name='monthly_audits'),
    path('audits/<int:audit_id>/', views.audit_detail, name='audit_detail'),
    path('create-audits/', views.create_monthly_audits, name='create_audits'),
]