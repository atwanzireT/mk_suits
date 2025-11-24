# assets/forms.py
from django import forms
from .models import Asset, AssetCategory, RoomAsset, AssetMaintenanceLog
from room_bookings.models import Room

class AssetCategoryForm(forms.ModelForm):
    class Meta:
        model = AssetCategory
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Electronics, Furniture'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class AssetForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = ['name', 'category', 'model', 'serial_number', 'purchase_date', 'warranty_expiry', 'cost']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'model': forms.TextInput(attrs={'class': 'form-control'}),
            'serial_number': forms.TextInput(attrs={'class': 'form-control'}),
            'purchase_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'warranty_expiry': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

class RoomAssetForm(forms.ModelForm):
    class Meta:
        model = RoomAsset
        fields = ['room', 'asset', 'quantity', 'installation_date', 'status', 'notes']
        widgets = {
            'room': forms.Select(attrs={'class': 'form-control'}),
            'asset': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'installation_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class QuickRoomAssetForm(forms.ModelForm):
    """Simplified form for quick asset assignment to rooms"""
    asset_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter asset name'}))
    category_name = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Category (optional)'}))
    
    class Meta:
        model = RoomAsset
        fields = ['room', 'quantity', 'installation_date', 'status', 'notes']
        widgets = {
            'room': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'installation_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

class AssetMaintenanceForm(forms.ModelForm):
    class Meta:
        model = AssetMaintenanceLog
        fields = ['room_asset', 'maintenance_type', 'description', 'technician', 'cost', 'next_maintenance_date']
        widgets = {
            'room_asset': forms.Select(attrs={'class': 'form-control'}),
            'maintenance_type': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe the maintenance work done...'}),
            'technician': forms.TextInput(attrs={'class': 'form-control'}),
            'cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'next_maintenance_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }