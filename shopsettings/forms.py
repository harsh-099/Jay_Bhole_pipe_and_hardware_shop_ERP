from django import forms
from .models import ShopSettings


class ShopSettingsForm(forms.ModelForm):

    class Meta:

        model = ShopSettings

        fields = "__all__"

        widgets = {

            "shop_name": forms.TextInput(attrs={
                "class": "form-control"
            }),

            "owner_name": forms.TextInput(attrs={
                "class": "form-control"
            }),

            "mobile": forms.TextInput(attrs={
                "class": "form-control"
            }),

            "gst_number": forms.TextInput(attrs={
                "class": "form-control"
            }),

            "address": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3
            }),

            "logo": forms.FileInput(attrs={
                "class": "form-control"
            }),

        }