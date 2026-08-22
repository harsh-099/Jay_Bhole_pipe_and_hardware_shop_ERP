from django import forms
from .models import Bill

class BillForm(forms.ModelForm):

    class Meta:

        model = Bill

        fields = [
            'customer',
            'payment_method'
        ]

        widgets = {

            'customer': forms.Select(attrs={
                'class': 'form-select'
            }),

            'payment_method': forms.Select(attrs={
                'class': 'form-select'
            }),

        }