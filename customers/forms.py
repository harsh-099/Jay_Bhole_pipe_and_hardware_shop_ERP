from django import forms
from .models import Customer

class CustomerForm(forms.ModelForm):

    class Meta:

        model = Customer

        fields = [
        'name',
        'mobile',
        'address',
        'udhari'
        ]
        widgets = {

            'name': forms.TextInput(attrs={
                'class':'form-control',
                'placeholder':'Customer Name'
            }),

            'mobile': forms.TextInput(attrs={
                'class':'form-control',
                'placeholder':'Mobile Number'
            }),

            'address': forms.Textarea(attrs={
                'class':'form-control',
                'rows':3,
                'placeholder':'Address'
            }),

            'udhari': forms.NumberInput(attrs={
                'class':'form-control',
                'placeholder':'Udhari Amount'
            }),

        }