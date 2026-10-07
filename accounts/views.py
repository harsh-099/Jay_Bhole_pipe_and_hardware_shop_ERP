from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import LoginForm
from shopsettings.models import ShopSettings


def login_view(request):

    if request.user.is_authenticated:
        return redirect("dashboard")

    form = LoginForm(request, data=request.POST or None)

    if request.method == "POST":

        if form.is_valid():

            user = form.get_user()

            # फक्त active user ला login करू द्या
            if not user.is_active:
                messages.error(
                    request,
                    "This account is inactive."
                )
                return redirect("login")

            login(request, user)

            messages.success(
                request,
                f"Welcome {user.first_name or user.username}"
            )

            return redirect("dashboard")

        else:

            messages.error(
                request,
                "Invalid Username or Password"
            )

    shop = ShopSettings.objects.first()

    return render(
        request,
        "login.html",
        {
            "form": form,
            "shop": shop,
        }
    )


def logout_view(request):

    logout(request)

    return redirect("login")