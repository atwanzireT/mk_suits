from django import forms
from .models import Customer, SaunaUser, RoomReservation

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = [
            'first_name',
            'last_name',
            'email',
            'phone_number',
            'NIN'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'NIN': forms.TextInput(attrs={'class': 'form-control'}),
        }


class SaunaUserForm(forms.ModelForm):
    class Meta:
        model = SaunaUser
        fields = [
            'customer_name',
            'gender',
            'service',
            'keys'
        ]
        widgets = {
            'customer_name': forms.TextInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'service': forms.Select(attrs={'class': 'form-control'}),
            'keys': forms.Select(attrs={'class': 'form-control'}),
        }


class RoomReservationForm(forms.ModelForm):
    class Meta:
        model = RoomReservation
        fields = [
            'room', 
            'customer',  # Assuming you're keeping it as a CharField
            'email',
            'phone_number',
            'NIN',
            'check_in_date', 
            'check_out_date', 
            'special_requests'
        ]
        widgets = {
            'room': forms.Select(attrs={'class': 'form-control'}),
            'customer': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'NIN': forms.TextInput(attrs={'class': 'form-control'}),
            'check_in_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'check_out_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'special_requests': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
