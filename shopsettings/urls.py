from django.urls import path
from . import views

urlpatterns = [

    path(
        "",
        views.shop_settings,
        name="shop_settings"
    ),

]