from django.urls import path
from . import views

urlpatterns = [

    path(
        '',
        views.stock_ledger,
        name='stock_ledger'
    ),

]