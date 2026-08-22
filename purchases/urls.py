from django.urls import path
from . import views

urlpatterns = [

    path(
        "add/",
        views.add_purchase,
        name="add_purchase"
    ),

    path(
        "add-item/<int:id>/",
        views.add_purchase_item,
        name="add_purchase_item"
    ),

    path(
        "remove-item/<int:id>/",
        views.remove_purchase_item,
        name="remove_purchase_item"
    ),

    path(
        "save/",
        views.save_purchase,
        name="save_purchase"
    ),

    path(
    "print/<int:id>/",
    views.print_purchase,
    name="print_purchase"
),

path(
    "pdf/<int:id>/",
    views.purchase_details,
    name="purchase_details"
),
path(
    "update-qty/<int:id>/",
    views.update_quantity,
    name="po_update_qty"
),

]