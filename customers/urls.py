from django.urls import path
from . import views

urlpatterns = [

    path('', views.customer_list, name='customer_list'),

    path('add/', views.add_customer, name='add_customer'),

    path(
        'edit/<int:id>/',
        views.edit_customer,
        name='edit_customer'
    ),

    path(
        'delete/<int:id>/',
        views.delete_customer,
        name='delete_customer'
    ),

    path(
        'ledger/<int:customer_id>/',
        views.customer_ledger,
        name='customer_ledger'
    ),
    path(
    'receive-payment/<int:customer_id>/',
    views.receive_payment,
    name='receive_payment'
),
path(
    "whatsapp-reminder/<int:customer_id>/",
    views.whatsapp_reminder,
    name="whatsapp_reminder",
),
path(
    "statement/<int:customer_id>/",
    views.customer_statement,
    name="customer_statement"
),
path(
    "ajax-save-customer/",
    views.ajax_save_customer,
    name="ajax_save_customer"
),

]