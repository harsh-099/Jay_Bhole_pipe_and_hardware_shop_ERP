from django.urls import path

from . import views

urlpatterns = [

    path(
        "",
        views.global_search,
        name="global_search"
    ),

]