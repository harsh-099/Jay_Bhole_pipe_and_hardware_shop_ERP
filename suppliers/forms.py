from django import forms

from .models import Supplier


class SupplierForm(forms.ModelForm):

    class Meta:

        model = Supplier

        fields = '__all__'

        widgets = {

            'name': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            ),

            'mobile': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            ),

            'address': forms.Textarea(
                attrs={
                    'class': 'form-control'
                }
            ),

            'balance': forms.NumberInput(
                attrs={
                    'class': 'form-control'
                }
            ),

        }