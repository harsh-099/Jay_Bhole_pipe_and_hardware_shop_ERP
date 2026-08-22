from django.urls import path
from . import views


urlpatterns = [

    path(
        "",
        views.purchase_order_list,
        name="purchase_order_list"
    ),

    path(
        "add/",
        views.add_purchase_order,
        name="add_purchase_order"
    ),

    path(
    "add-item/<int:id>/",
    views.add_item,
    name="po_add_item"
),

path(
    "remove-item/<int:id>/",
    views.remove_item,
    name="po_remove_item"
),

path(
    "save/",
    views.save_purchase_order,
    name="save_purchase_order"
),
path(
    "view/<int:id>/",
    views.view_purchase_order,
    name="view_purchase_order"
),

path(
    "convert/<int:id>/",
    views.convert_to_purchase,
    name="convert_to_purchase"
),
path(
    "update-qty/<int:id>/",
     view=views.update_quantity,
    name="update_quantity"
),
path(
    "clear-cart/",
    views.clear_po_cart,
    name="clear_po_cart",
),
path(
    "print/<int:id>/",
    views.print_purchase_order,
    name="print_purchase_order"
),
]