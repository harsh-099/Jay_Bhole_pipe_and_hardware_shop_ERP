from django.shortcuts import render
from products.models import Product
from customers.models import Customer
from billing.models import Bill
from expenses.models import Expense
from django.db.models import Sum
from django.db.models.functions import TruncMonth
import json
from django.contrib.auth.decorators import login_required
from purchases.models import Purchase
from billing.models import BillItem
from datetime import date
from django.db.models import Sum
from decimal import Decimal
from accounts.decorators import allowed_roles
from advisor.utils import get_business_advice
from django.utils import timezone
from advisor.utils import (
    get_business_advice,
    get_business_brief,
    get_health_score,
    get_purchase_recommendations,
    get_dead_stock,
)

@login_required
@allowed_roles(roles=["Admin", "Manager"])
def dashboard(request):

    total_products = Product.objects.count()

    total_customers = Customer.objects.count()

    # Total Sales
    total_sales = sum(
        bill.total_amount
        for bill in Bill.objects.all()
    )

# Payment Count
    cash_count = Bill.objects.filter(
        payment_method="Cash"
    ).count()

    upi_count = Bill.objects.filter(
        payment_method="UPI"
    ).count()

    credit_count = Bill.objects.filter(
        payment_method="Credit"
    ).count()

    # Total Purchase
    total_purchase = sum(
        purchase.total_amount
        for purchase in Purchase.objects.all()
    )

    # Total Expense
    total_expense = sum(
        expense.amount
        for expense in Expense.objects.all()
    )

    # Customer Credit
    total_udhari = sum(
        customer.credit_balance
        for customer in Customer.objects.all()
    )

   # -----------------------------
    # Gross Profit
    # -----------------------------

    gross_profit = Decimal("0")

    bill_items = BillItem.objects.all()

    for item in bill_items:

        gross_profit += (
            (item.price - item.purchase_price)
            * item.quantity
        )

    # -----------------------------
    # Net Profit
    # -----------------------------

    profit = gross_profit - Decimal(total_expense)


    recent_bills = Bill.objects.order_by(
        '-id'
    )[:5]
    recent_purchases = Purchase.objects.select_related(
    'supplier'
    ).order_by('-id')[:5]

    low_stock = Product.objects.filter(
        quantity__lte=10
    )
    monthly_sales = (

    Bill.objects

    .annotate(
        month=TruncMonth('created_at')
    )

    .values('month')

    .annotate(
        total=Sum('total_amount')
    )

    .order_by('month')

    )

    chart_labels = []

    chart_data = []

    for row in monthly_sales:

        if row["month"]:
            chart_labels.append(row["month"].strftime("%b"))
            chart_data.append(float(row["total"] or 0))
    today = date.today()

    low_stock = Product.objects.filter(
        quantity__lte=10
    ).order_by("quantity")

    low_stock_count = low_stock.count()

    low_stock = low_stock[:3]

    pending_udhari = sum(
        customer.credit_balance
        for customer in Customer.objects.all()
    )

    today_sales = Bill.objects.filter(
        created_at__date=today
    ).aggregate(
        total=Sum("total_amount")
    )["total"] or 0

    today_expenses = Expense.objects.filter(
        date=today
    ).aggregate(
        total=Sum("amount")
    )["total"] or 0

    today_bill_count = Bill.objects.filter(
        created_at__date=today
    ).count()

    from datetime import datetime

    current_month = today.month

    current_year = today.year

    month_sales = Bill.objects.filter(

        created_at__month=current_month,

        created_at__year=current_year

    ).aggregate(

        total=Sum("total_amount")

    )["total"] or 0

    month_expenses = Expense.objects.filter(

        date__month=current_month,

        date__year=current_year

    ).aggregate(

        total=Sum("amount")

    )["total"] or 0

    today_profit = profit

    context = {

        'total_products': total_products,

        'total_customers': total_customers,

        'total_sales': total_sales,
        'total_purchase': total_purchase,

        'total_udhari': total_udhari,

        'total_expense': total_expense,

        'profit': profit,

        'recent_bills': recent_bills,
        'recent_purchases': recent_purchases,


        'low_stock': low_stock,
        'chart_labels': json.dumps(chart_labels),

        'chart_data': json.dumps(chart_data),
        'cash_count': cash_count,
        'upi_count': upi_count,
        'credit_count': credit_count,
        'low_stock': low_stock,
        'low_stock_count': low_stock_count,

        'pending_udhari': pending_udhari,

        'today_sales': today_sales,

        'today_expenses': today_expenses,
        'today_bill_count': today_bill_count,

    'month_sales': month_sales,

    'month_expenses': month_expenses,

    'today_profit': today_profit,
    'advisor': get_business_advice(),
    'brief': get_business_brief(),
    'health_score': get_health_score(),
    'purchase_advice': get_purchase_recommendations(),
    'dead_stock': get_dead_stock(),
    'now': timezone.now(),
    }

    return render(
        request,
        'dashboard.html',
        context
    )