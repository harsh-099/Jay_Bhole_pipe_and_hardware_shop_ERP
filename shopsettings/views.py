from django.shortcuts import render, redirect
from .models import ShopSettings
from .forms import ShopSettingsForm
from accounts.decorators import allowed_roles

@allowed_roles(roles=["Admin"])
def shop_settings(request):

    settings = ShopSettings.objects.first()

    if request.method == "POST":

        if settings:

            form = ShopSettingsForm(
                request.POST,
                request.FILES,
                instance=settings
            )

        else:

            form = ShopSettingsForm(
                request.POST,
                request.FILES
            )

        if form.is_valid():

            form.save()

            return redirect("shop_settings")

    else:

        if settings:

            form = ShopSettingsForm(
                instance=settings
            )

        else:

            form = ShopSettingsForm()

    return render(

        request,

        "shopsettings/settings.html",

        {

            "form": form

        }

    )