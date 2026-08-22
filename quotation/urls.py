from django.urls import path
from . import views

urlpatterns = [

    path(
        "",
        views.quotation_list,
        name="quotation_list"
    ),

    path(
        "add/",
        views.add_quotation,
        name="add_quotation"
    ),

    path(
        "save/", views.save_quotation, name="save_quotation"
    ),
    
    path(
    "add-product/<int:product_id>/",
    views.add_to_quotation,
    name="add_to_quotation"
),

path(
    "increase/<int:product_id>/",
    views.increase_qty,
    name="quotation_increase_qty"
),

path(
    "decrease/<int:product_id>/",
    views.decrease_qty,
    name="quotation_decrease_qty"
),

path(
    "remove/<int:product_id>/",
    views.remove_item,
    name="quotation_remove_item"
),
path(
    "<int:id>/",
    views.quotation_detail,
    name="quotation_detail"
),

path(
    "pdf/<int:id>/",
    views.quotation_pdf,
    name="quotation_pdf"
),

path(
    "delete/<int:id>/",
    views.delete_quotation,
    name="delete_quotation"
),
path(
    "convert/<int:id>/",
    views.convert_to_bill,
    name="convert_to_bill"
),

]