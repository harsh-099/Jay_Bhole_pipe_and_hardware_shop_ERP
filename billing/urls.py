from django.urls import path
from . import views

urlpatterns = [

    path('', views.billing, name='billing'),

    path(
        'add/<int:product_id>/',
        views.add_to_bill,
        name='add_to_bill'
    ),
    path(
    'increase/<int:product_id>/',
    views.increase_qty,
    name='increase_qty'
),

path(
    'decrease/<int:product_id>/',
    views.decrease_qty,
    name='decrease_qty'
),

path(
    'remove/<int:product_id>/',
    views.remove_item,
    name='remove_item'
),
path(
    'save/',
    views.save_bill,
    name='save_bill'
),
path(
    'invoice/<int:bill_id>/',
    views.invoice_detail,
    name='invoice_detail'
),


path(
    'download/<int:bill_id>/',
    views.download_invoice,
    name='download_invoice'
),
path(
    'update/<int:product_id>/',
    views.update_qty,
    name='update_qty'),
]