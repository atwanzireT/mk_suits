

# assets/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from room_bookings.models import Room

class AssetCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name

class Asset(models.Model):
    ASSET_STATUS = [
        ('working', 'Working'),
        ('maintenance', 'Needs Maintenance'),
        ('broken', 'Broken'),
        ('replaced', 'Replaced'),
    ]
    
    name = models.CharField(max_length=100)
    category = models.ForeignKey(AssetCategory, on_delete=models.CASCADE)
    model = models.CharField(max_length=100, blank=True)
    serial_number = models.CharField(max_length=100, blank=True, null=True, unique=True)
    purchase_date = models.DateField(default=timezone.now)
    warranty_expiry = models.DateField(null=True, blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    def __str__(self):
        return f"{self.name} ({self.model})"

class RoomAsset(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='room_assets')
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    installation_date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=20, choices=Asset.ASSET_STATUS, default='working')
    notes = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['room', 'asset']
    
    def __str__(self):
        return f"{self.room.room_number} - {self.asset.name}"

class AssetMaintenanceLog(models.Model):
    room_asset = models.ForeignKey(RoomAsset, on_delete=models.CASCADE, related_name='maintenance_logs')
    maintenance_date = models.DateTimeField(default=timezone.now)
    maintenance_type = models.CharField(max_length=50, choices=[
        ('routine', 'Routine Check'),
        ('repair', 'Repair'),
        ('replacement', 'Replacement'),
        ('cleaning', 'Cleaning'),
    ])
    description = models.TextField()
    technician = models.CharField(max_length=100)
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    next_maintenance_date = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.room_asset} - {self.maintenance_type}"

class MonthlyAudit(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    audit_date = models.DateField(default=timezone.now)
    auditor = models.ForeignKey(User, on_delete=models.CASCADE)
    notes = models.TextField(blank=True)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['room', 'audit_date']
        ordering = ['-audit_date']
    
    def __str__(self):
        return f"Audit - {self.room.room_number} ({self.audit_date})"

class AuditItem(models.Model):
    audit = models.ForeignKey(MonthlyAudit, on_delete=models.CASCADE, related_name='audit_items')
    room_asset = models.ForeignKey(RoomAsset, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=Asset.ASSET_STATUS)
    condition_notes = models.TextField(blank=True)
    photo = models.ImageField(upload_to='asset_audits/%Y/%m/', blank=True, null=True)
    
    def __str__(self):
        return f"{self.room_asset} - {self.status}"