from django import forms
from .models import Revenue, Expense, Asset, Liability


class RevenueForm(forms.ModelForm):
    class Meta:
        model = Revenue
        fields = ['category', 'description', 'amount', 'received_from', 'date']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'received_from': forms.TextInput(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['category', 'description', 'amount', 'date', 'drawn_by']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'drawn_by': forms.TextInput(attrs={'class': 'form-control'}),
        }


class AssetForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = ['name', 'location', 'value', 'date_acquired']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'value': forms.NumberInput(attrs={'class': 'form-control'}),
            'date_acquired': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class LiabilityForm(forms.ModelForm):
    class Meta:
        model = Liability
        fields = ['name', 'amount', 'due_date']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
