from django.urls import path
from . import views

urlpatterns = [

    path(
        'sales/',
        views.sales_report,
        name='sales_report'
    ),

    path(
        'stock/',
        views.stock_report,
        name='stock_report'
    ),

    path(
        'top-products/',
        views.top_products_report,
        name='top_products_report'
    ),

    path(
        'sales/pdf/',
        views.sales_report_pdf,
        name='sales_report_pdf'
    ),

    path(
        'expenses/',
        views.expense_report,
        name='expense_report'
    ),

    path(
        'profit/',
        views.profit_report,
        name='profit_report'
    ),

    # ✅ Payment Recovery
    path(
        'payment-recovery/',
        views.payment_recovery,
        name='payment_recovery'
    ),
    path(
    "purchase/",
    views.purchase_report,
    name="purchase_report"
),

path(
    "purchase/pdf/",
    views.purchase_report_pdf,
    name="purchase_report_pdf"
),
path( "stock/pdf/", views.stock_report_pdf, name="stock_report_pdf" ),

path(
    "expenses/pdf/",
    views.expense_report_pdf,
    name="expense_report_pdf"
),

path(
    "profit/pdf/",
    views.profit_report_pdf,
    name="profit_report_pdf"
),

path("top-products/pdf/", views.top_products_pdf, name="top_products_pdf"),

path(
    "low-stock/",
    views.low_stock_report,
    name="low_stock_report"
),
path('low-stock/pdf/', views.low_stock_pdf, name='low_stock_pdf'),
path(
    "payment-recovery/pdf/",
    views.payment_recovery_pdf,
    name="payment_recovery_pdf"
),
path(
    "daily-sales/",
    views.daily_sales_report,
    name="daily_sales_report"
),

path(
    "daily-sales/pdf/",
    views.daily_sales_pdf,
    name="daily_sales_pdf"
),

path(
    "monthly-sales/",
    views.monthly_sales_report,
    name="monthly_sales_report"
),
path(
    "monthly-sales/pdf/",
    views.monthly_sales_pdf,
    name="monthly_sales_pdf"
),
path(
    "customer-ledger/",
    views.customer_ledger_report,
    name="customer_ledger_report"
),
path(
    "customer-ledger/pdf/",
    views.customer_ledger_pdf,
    name="customer_ledger_pdf"
),


path(
    "supplier-ledger/",
    views.supplier_ledger_report,
    name="supplier_ledger_report"
),

path(
    "supplier-ledger/",
    views.supplier_ledger_report,
    name="supplier_ledger_report"
),

path(
    "supplier-ledger/pdf/",
    views.supplier_ledger_pdf,
    name="supplier_ledger_pdf"
),
path(
    "best-customers/",
    views.best_customers_report,
    name="best_customers_report"
),
path(
    "best-customers/pdf/",
    views.best_customers_pdf,
    name="best_customers_pdf"
),

path(
    "best-suppliers/",
    views.best_suppliers_report,
    name="best_suppliers_report"
),

path(
    "best-suppliers/pdf/",
    views.best_suppliers_pdf,
    name="best_suppliers_pdf"
),

path(
    "payment-mode/",
    views.payment_mode_report,
    name="payment_mode_report"
),
path(
    "payment-mode/pdf/",
    views.payment_mode_pdf,
    name="payment_mode_pdf"
),
path(
    "dead-stock/",
    views.dead_stock_report,
    name="dead_stock_report"
),
path(
    "dead-stock/print/",
    views.print_dead_stock_report,
    name="print_dead_stock_report"
),
path(
    "business-position/",
    views.business_position_report,
    name="business_position_report",
),
path(
    "business-position/print/",
    views.print_business_position_report,
    name="print_business_position_report",
),

]