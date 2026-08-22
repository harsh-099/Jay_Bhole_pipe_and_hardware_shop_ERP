from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import LoginForm
from shopsettings.models import ShopSettings
from django.contrib.auth.models import User
from .models import UserProfile
from .forms import UserForm, UserProfileForm
from django.contrib.auth.models import Group
from accounts.decorators import allowed_roles
from accounts.decorators import allowed_roles


def login_view(request):

    if request.user.is_authenticated:
        return redirect("dashboard")

    form = LoginForm(request, data=request.POST or None)

    if request.method == "POST":

        if form.is_valid():

            user = form.get_user()
            login(request, user)

            messages.success(
                request,
                f"Welcome {user.first_name or user.username}"
            )

            # -----------------------------
            # Role Based Redirect
            # -----------------------------

            if user.is_superuser:
                return redirect("dashboard")

            elif user.groups.filter(name="Admin").exists():
                return redirect("dashboard")

            elif user.groups.filter(name="Manager").exists():
                return redirect("dashboard")

            elif user.groups.filter(name="Cashier").exists():
                return redirect("billing")

            elif user.groups.filter(name="Store").exists():
                return redirect("add_purchase")

            elif user.groups.filter(name="Accountant").exists():
                return redirect("expense_list")     # किंवा reports_dashboard

            elif user.groups.filter(name="Reports").exists():
                return redirect("reports_home")     # तुझा reports page

            else:
                messages.error(
                    request,
                    "No role assigned to this user."
                )
                logout(request)
                return redirect("login")
            
        else:

            messages.error(
                request,
                "Invalid Username or Password"
            )
    shop = ShopSettings.objects.first()

    return render(

        request,

        "accounts/login.html",

        {

            "form": form,
            "shop": shop,

        }

    )


def logout_view(request):

    logout(request)

    return redirect("login")


@allowed_roles(roles=["Admin"])
def users(request):

    users = User.objects.select_related(
        "profile"
    ).order_by("first_name")

    return render(

        request,

        "accounts/users.html",

        {

            "users": users

        }

    )

@allowed_roles(["Admin"])
def add_user(request):

    if request.method == "POST":

        user_form = UserForm(request.POST)

        profile_form = UserProfileForm(
            request.POST,
            request.FILES
        )

        if user_form.is_valid() and profile_form.is_valid():

            user = user_form.save()

            profile = user.profile

            profile.role = profile_form.cleaned_data["role"]

            group_name = profile.role

            group, created = Group.objects.get_or_create(
                name=group_name
            )

            user.groups.clear()

            user.groups.add(group)


            profile.mobile = profile_form.cleaned_data["mobile"]

            profile.address = profile_form.cleaned_data["address"]

            profile.photo = profile_form.cleaned_data["photo"]

            profile.is_active = profile_form.cleaned_data["is_active"]

            profile.email = user.email

            profile.save()

            messages.success(
                request,
                "User Created Successfully."
            )

            return redirect("users")

    else:

        user_form = UserForm()

        profile_form = UserProfileForm()

    return render(

        request,

        "accounts/add_user.html",

        {

            "user_form": user_form,

            "profile_form": profile_form,

        }

    )

from django.shortcuts import get_object_or_404

@allowed_roles(["Admin"])
def edit_user(request, id):

    user = get_object_or_404(
        User,
        id=id
    )

    profile = user.profile

    if request.method == "POST":

        user.first_name = request.POST.get("first_name")

        user.last_name = request.POST.get("last_name")

        user.username = request.POST.get("username")

        user.email = request.POST.get("email")

        user.save()

        profile.role = request.POST.get("role")

        group_name = profile.role

        group, created = Group.objects.get_or_create(
            name=group_name
        )

        user.groups.clear()

        user.groups.add(group)


        profile.mobile = request.POST.get("mobile")

        profile.address = request.POST.get("address")

        profile.is_active = (
            "is_active" in request.POST
        )

        if request.FILES.get("photo"):

            profile.photo = request.FILES.get(
                "photo"
            )

        profile.save()

        messages.success(

            request,

            "User Updated Successfully."

        )

        return redirect("users")

    return render(

        request,

        "accounts/edit_user.html",

        {

            "user": user,

            "profile": profile,

            "roles": UserProfile.ROLE_CHOICES,

        }

    )

from django.contrib.auth.forms import SetPasswordForm

@allowed_roles(["Admin"])
def delete_user(request, id):

    user = get_object_or_404(
        User,
        id=id
    )

    if user.is_superuser:

        messages.error(
            request,
            "Super Admin cannot be deleted."
        )

        return redirect("users")

    user.delete()

    messages.success(
        request,
        "User Deleted Successfully."
    )

    return redirect("users")


@allowed_roles(["Admin"])
def change_password(request, id):

    user = get_object_or_404(
        User,
        id=id
    )

    if request.method == "POST":

        form = SetPasswordForm(
            user,
            request.POST
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Password Changed Successfully."
            )

            return redirect("users")

    else:

        form = SetPasswordForm(user)

    return render(

        request,

        "accounts/change_password.html",

        {

            "form": form,

            "user_obj": user

        }

    )
