from django.urls import path
from . import views

urlpatterns = [

    path(
        "",
        views.activity_logs,
        name="activity_logs"
    ),

]