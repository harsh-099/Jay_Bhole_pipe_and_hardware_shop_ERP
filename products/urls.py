from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('add/', views.add_product, name='add_product'),
    path('edit/<int:id>/', views.edit_product, name='edit_product'),
    path('delete/<int:id>/', views.delete_product, name='delete_product'),
    path(
    "export/",
    views.export_products_excel,
    name="export_products_excel"
),

path(
    "import/",
    views.import_products_excel,
    name="import_products_excel"
),
path(
    "low-stock/",
    views.low_stock_products,
    name="low_stock_products"
),
]