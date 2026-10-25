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
from django.utils import timezone
from advisor.utils import (
    get_business_brief,
    get_health_score,
   
)
from django.db.models import Count
from decimal import Decimal
from django.db.models import Sum, F, DecimalField, ExpressionWrapper

@login_required
@allowed_roles(roles=["Admin", "Manager"])

def dashboard(request):

    # -----------------------------
    # Basic Counts
    # -----------------------------
    total_products = Product.objects.count()
    total_customers = Customer.objects.count()

    # -----------------------------
    # Total Sales, Purchase & Expense
    # -----------------------------
    total_sales = (
        Bill.objects.aggregate(total=Sum("total_amount"))["total"]
        or Decimal("0")
    )

    total_purchase = (
        Purchase.objects.aggregate(total=Sum("total_amount"))["total"]
        or Decimal("0")
    )

    total_expense = (
        Expense.objects.aggregate(total=Sum("amount"))["total"]
        or Decimal("0")
    )
    # Total Sales after Expenses
    sales_after_expenses = total_sales - total_expense

    # -----------------------------
    # Payment Counts
    # -----------------------------
    payment_counts = {
    row["payment_method"]: row["count"]
    for row in (
        Bill.objects
        .values("payment_method")
        .annotate(count=Count("id"))
    )
}

    cash_count = payment_counts.get("Cash", 0)
    upi_count = payment_counts.get("UPI", 0)
    credit_count = payment_counts.get("Credit", 0)

    # -----------------------------
    # Customer Credit
    # -----------------------------
    total_udhari = (
        Customer.objects.aggregate(
            total=Sum("credit_balance")
        )["total"]
        or Decimal("0")
    )

    pending_udhari = total_udhari

    # -----------------------------
    # Gross Profit
    # -----------------------------
    profit_expression = ExpressionWrapper(
        (F("price") - F("purchase_price")) * F("quantity"),
        output_field=DecimalField(
            max_digits=20,
            decimal_places=2,
        ),
    )

    gross_profit = (
        BillItem.objects.aggregate(
            total=Sum(profit_expression)
        )["total"]
        or Decimal("0")
    )

    profit = gross_profit

    # -----------------------------
    # Recent Records
    # -----------------------------
    recent_bills = Bill.objects.order_by("-id")[:5]

    recent_purchases = (
        Purchase.objects
        .select_related("supplier")
        .order_by("-id")[:5]
    )

    # -----------------------------
    # Low Stock
    # -----------------------------
    low_stock_queryset = Product.objects.filter(
        quantity__lte=10
    ).order_by("quantity")

    low_stock_count = low_stock_queryset.count()
    low_stock = low_stock_queryset[:3]

    # -----------------------------
    # Monthly Sales Chart
    # -----------------------------
    monthly_sales = (
        Bill.objects
        .annotate(month=TruncMonth("created_at"))
        .values("month")
        .annotate(total=Sum("total_amount"))
        .order_by("month")
    )

    chart_labels = []
    chart_data = []

    for row in monthly_sales:
        if row["month"]:
            chart_labels.append(row["month"].strftime("%b"))
            chart_data.append(float(row["total"] or 0))

    # -----------------------------
    # Today's Statistics
    # -----------------------------
    today = date.today()

    today_sales = (
        Bill.objects.filter(created_at__date=today)
        .aggregate(total=Sum("total_amount"))["total"]
        or Decimal("0")
    )

    today_expenses = (
        Expense.objects.filter(date=today)
        .aggregate(total=Sum("amount"))["total"]
        or Decimal("0")
    )

    today_bill_count = Bill.objects.filter(
        created_at__date=today
    ).count()

    # -----------------------------
    # Current Month Statistics
    # -----------------------------
    current_month = today.month
    current_year = today.year

    month_sales = (
        Bill.objects.filter(
            created_at__month=current_month,
            created_at__year=current_year,
        ).aggregate(total=Sum("total_amount"))["total"]
        or Decimal("0")
    )

    month_expenses = (
        Expense.objects.filter(
            date__month=current_month,
            date__year=current_year,
        ).aggregate(total=Sum("amount"))["total"]
        or Decimal("0")
    )

    # Keep existing behavior
    today_profit = profit

    # -----------------------------
    # Dashboard Context
    # -----------------------------
    context = {
        "total_products": total_products,
        "total_customers": total_customers,
        "total_sales": total_sales,
        "sales_after_expenses": sales_after_expenses,
        "total_purchase": total_purchase,
        "total_udhari": total_udhari,
        "total_expense": total_expense,
        "profit": profit,
        "recent_bills": recent_bills,
        "recent_purchases": recent_purchases,
        "low_stock": low_stock,
        "low_stock_count": low_stock_count,
        "chart_labels": json.dumps(chart_labels),
        "chart_data": json.dumps(chart_data),
        "cash_count": cash_count,
        "upi_count": upi_count,
        "credit_count": credit_count,
        "pending_udhari": pending_udhari,
        "today_sales": today_sales,
        "today_expenses": today_expenses,
        "today_bill_count": today_bill_count,
        "month_sales": month_sales,
        "month_expenses": month_expenses,
        "today_profit": today_profit,
        "now": timezone.now(),
    }

    return render(request, "dashboard.html", context)
