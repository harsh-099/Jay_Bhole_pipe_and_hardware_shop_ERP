from django.urls import path
from . import views

urlpatterns = [

    path(
        '',
        views.purchase_return_list,
        name='purchase_return_list'
    ),

    path(
        'create/<int:purchase_id>/',
        views.purchase_return,
        name='purchase_return'
    ),

    path(
        'pdf/<int:return_id>/',
        views.purchase_return_pdf,
        name='purchase_return_pdf'
    ),

    path(
        'print/<int:return_id>/',
        views.purchase_return_print,
        name='purchase_return_print'
    ),

]