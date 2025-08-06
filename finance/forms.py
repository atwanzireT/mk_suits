from datetime import date, datetime
from .models import Budget, BudgetLine, LiabilityPayment
from django import forms
from .models import Revenue, Expense, Asset, Liability

class RevenueForm(forms.ModelForm):
    class Meta:
        model = Revenue
        fields = ['category', 'description', 'amount', 'received_from', 'date', 'attachment']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'received_from': forms.TextInput(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'attachment': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['category', 'description', 'amount', 'date', 'attachment']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'drawn_by': forms.TextInput(attrs={'class': 'form-control'}),
            'attachment': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class AssetForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = ['name', 'value','life_years', 'purchase_date', 'attachment'] 
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'value': forms.NumberInput(attrs={'class': 'form-control'}),
            'life_years':forms.NumberInput(attrs={'class':'form-control'}),
            'purchase_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}), 
            'attachment': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


class LiabilityForm(forms.ModelForm):
    class Meta:
        model = Liability
        fields = ['description', 'category', 'amount', 'date_received',
                  'due_date', 'attachment', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Enter a brief description of the liability...'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Enter amount in UGX...'
            }),
            'date_received': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'due_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'attachment': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount is not None and amount <= 0:
            raise forms.ValidationError("Amount must be greater than zero.")
        return amount


    def clean_due_date(self):
        due_date = self.cleaned_data.get('due_date')
        if due_date and due_date < date.today():  # <- FIXED with date.today()
            raise forms.ValidationError("Due date cannot be in the past.")
        return due_date
    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.pk:
            instance.remaining_balance = instance.amount  # Set initial balance on creation
        if commit:
            instance.save()
        return instance

MONTH_CHOICES = [
    (1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'),
    (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'),
    (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December'),
]
 
class BudgetForm(forms.ModelForm):
    month = forms.ChoiceField(
        choices=MONTH_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Budget
        fields = ['month', 'year', 'revenue_estimate',
                  'expense_estimate', 'start_date', 'end_date']
        widgets = {
            'month': forms.Select(attrs={
                'class': 'form-select',
            }),
            'year': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Year',
                'min': 2000,
                'max': 2100,
            }),
            'revenue_estimate': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Estimated Revenue',
                'step': '0.01',
            }),
            'expense_estimate': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Estimated Expenses',
                'step': '0.01',
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }


class BudgetLineForm(forms.ModelForm):
    class Meta:
        model = BudgetLine
        fields = ['budget', 'category', 'estimated_amount']


class LiabilityPaymentForm(forms.ModelForm):
    class Meta:
        model = LiabilityPayment
        fields = ['amount_paid', 'new_due_date', 'notes']
        
        widgets = {
            'new_due_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'amount_paid': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Enter amount in UGX...'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Enter a brief description of the liability...'
            }),
        }