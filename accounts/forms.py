from django import forms
from django.contrib.auth.forms import AuthenticationForm


class LoginForm(AuthenticationForm):

    username = forms.CharField(

        widget=forms.TextInput(

            attrs={

                "class": "form-control",

                "placeholder": "Username",

                "autocomplete": "username",

            }

        )

    )

    password = forms.CharField(

        widget=forms.PasswordInput(

            attrs={

                "class": "form-control",

                "placeholder": "Password",

                "id": "password",

                "autocomplete": "current-password",

            }

        )

    )

from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from .models import UserProfile


class UserForm(UserCreationForm):

    first_name = forms.CharField(
        max_length=100,
        required=True
    )

    last_name = forms.CharField(
        max_length=100,
        required=False
    )

    email = forms.EmailField(
        required=False
    )

    class Meta:

        model = User

        fields = (

            "first_name",

            "last_name",

            "username",

            "email",

            "password1",

            "password2",

        )


class UserProfileForm(forms.ModelForm):

    class Meta:

        model = UserProfile

        fields = (

            "role",

            "mobile",

            "address",

            "photo",

            "is_active",

        )
