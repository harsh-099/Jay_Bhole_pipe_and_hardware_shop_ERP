from django.urls import path

from . import views


urlpatterns = [

    path(
        '',
        views.supplier_list,
        name='supplier_list'
    ),

    path(
        'add/',
        views.add_supplier,
        name='add_supplier'
    ),
    path(
    'edit/<int:id>/',
    views.edit_supplier,
    name='edit_supplier'
),

path(
    'delete/<int:id>/',
    views.delete_supplier,
    name='delete_supplier'
),
path(
    "ledger/<int:supplier_id>/",
    views.supplier_ledger,
    name="supplier_ledger"
),
path(
    "ledger/pdf/<int:supplier_id>/",
    views.supplier_ledger_pdf,
    name="supplier_ledger_pdf"
),

path(
    "ledger/print/<int:supplier_id>/",
    views.supplier_ledger_print,
    name="supplier_ledger_print"
),
]