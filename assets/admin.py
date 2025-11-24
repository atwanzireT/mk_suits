# assets/admin.py
from django.contrib import admin
from .models import AssetCategory, Asset, RoomAsset, AssetMaintenanceLog, MonthlyAudit, AuditItem

@admin.register(AssetCategory)
class AssetCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']

@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'model', 'purchase_date']
    list_filter = ['category', 'purchase_date']
    search_fields = ['name', 'model', 'serial_number']

@admin.register(RoomAsset)
class RoomAssetAdmin(admin.ModelAdmin):
    list_display = ['room', 'asset', 'quantity', 'status', 'installation_date']
    list_filter = ['status', 'room', 'installation_date']
    search_fields = ['asset__name', 'room__room_number']

admin.site.register(AssetMaintenanceLog)
admin.site.register(MonthlyAudit)
admin.site.register(AuditItem)