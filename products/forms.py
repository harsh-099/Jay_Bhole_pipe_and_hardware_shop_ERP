from django import forms
from .models import Product


class ProductForm(forms.ModelForm):

    class Meta:

        model = Product

        fields = "__all__"

        widgets = {

            "name": forms.TextInput(attrs={
                "class": "form-control"
            }),

            "category": forms.TextInput(attrs={
                "class": "form-control"
            }),

            "purchase_price": forms.NumberInput(attrs={
                "class": "form-control"
            }),

            "selling_price": forms.NumberInput(attrs={
                "class": "form-control"
            }),

            "quantity": forms.NumberInput(attrs={
                "class": "form-control"
            }),

            "unit": forms.Select(

                choices=[

                    ("Piece", "Piece"),

                    ("Meter", "Meter"),

                    ("Kg", "Kg"),

                    ("Box", "Box"),

                    ("Bundle", "Bundle"),

                ],

                attrs={
                    "class": "form-select"
                }

            )

        }

    def clean_name(self):

        name = self.cleaned_data["name"].strip()

        qs = Product.objects.filter(
            name__iexact=name
        )

        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():

            raise forms.ValidationError(
                "This product already exists."
            )

        return name