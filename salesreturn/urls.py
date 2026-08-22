from django.urls import path
from . import views
from django.shortcuts import render, get_object_or_404
from shopsettings.models import ShopSettings

from .models import SaleReturn

urlpatterns = [

    path(
        '',
        views.sale_return_list,
        name='sale_return_list'
    ),

    path(
        'create/<int:bill_id>/',
        views.sale_return,
        name='sale_return'
    ),

path(

    "print/<int:id>/",

    views.print_sale_return,

    name="print_sale_return",

),

path(

    "pdf/<int:return_id>/",

    views.sale_return_pdf,

    name="sale_return_pdf",

),
]