from django.urls import path
from . import views

urlpatterns = [

    path(
        "login/",
        views.login_view,
        name="login"
    ),

    path(
        "logout/",
        views.logout_view,
        name="logout"
    ),
path(
    "users/",
    views.users,
    name="users"
),

path(
    "users/add/",
    views.add_user,
    name="add_user"
),

path(

    "users/edit/<int:id>/",

    views.edit_user,

    name="edit_user"

),

path(
    "users/delete/<int:id>/",
    views.delete_user,
    name="delete_user"
),

path(
    "users/change-password/<int:id>/",
    views.change_password,
    name="change_password"
),



]
