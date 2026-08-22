from django.db.models import Sum
from products.models import Product
from customers.models import Customer
from billing.models import BillItem


def get_business_advice():

    advice = []

    # -----------------------------
    # Low Stock Alert
    # -----------------------------
    low_stock = Product.objects.filter(
        quantity__lte=10
    ).count()

    if low_stock:

        advice.append({

            "icon": "fa-box-open",

            "color": "warning",

            "title": "Low Stock",

            "message": f"{low_stock} products need restocking."

        })

    # -----------------------------
    # Highest Credit Customer
    # -----------------------------
    customer = Customer.objects.order_by(
        "-credit_balance"
    ).first()

    if customer and customer.credit_balance > 0:

        advice.append({

            "icon": "fa-money-bill-wave",

            "color": "danger",

            "title": "Pending Recovery",

            "message": f"{customer.name} has ₹{customer.credit_balance} pending."

        })

    # -----------------------------
    # Top Selling Product
    # -----------------------------
    top_product = (

        BillItem.objects

        .values("product__name")

        .annotate(total_qty=Sum("quantity"))

        .order_by("-total_qty")

        .first()

    )

    if top_product:

        advice.append({

            "icon": "fa-fire",

            "color": "success",

            "title": "Top Selling Product",

            "message": f'{top_product["product__name"]} ({top_product["total_qty"]} sold)'

        })

    return advice

from django.db.models import Sum
from datetime import date, timedelta
from billing.models import Bill
from expenses.models import Expense


def get_business_brief():

    today = date.today()

    yesterday = today - timedelta(days=1)

    # ------------------------
    # Today's Sales
    # ------------------------

    today_sales = Bill.objects.filter(
        created_at__date=today
    ).aggregate(
        total=Sum("final_amount")
    )["total"] or 0

    # ------------------------
    # Yesterday Sales
    # ------------------------

    yesterday_sales = Bill.objects.filter(
        created_at__date=yesterday
    ).aggregate(
        total=Sum("final_amount")
    )["total"] or 0

    # ------------------------
    # Today's Expense
    # ------------------------

    today_expense = Expense.objects.filter(
        date=today
    ).aggregate(
        total=Sum("amount")
    )["total"] or 0

    # ------------------------
    # Bills Count
    # ------------------------

    bills = Bill.objects.filter(
        created_at__date=today
    ).count()

    # ------------------------
    # Trend
    # ------------------------

    if today_sales > yesterday_sales:

        trend = "📈 Sales Increased"

    elif today_sales < yesterday_sales:

        trend = "📉 Sales Decreased"

    else:

        trend = "➡ Sales Same"

    return {

        "today_sales": today_sales,

        "today_expense": today_expense,

        "bills": bills,

        "trend": trend,

    }


from decimal import Decimal
from products.models import Product
from customers.models import Customer
from billing.models import Bill
from expenses.models import Expense
from django.db.models import Sum
from datetime import date


def get_health_score():

    score = 100

    today = date.today()

    # -----------------------
    # Low Stock
    # -----------------------

    low_stock = Product.objects.filter(
        quantity__lte=10
    ).count()

    score -= low_stock * 2

    # -----------------------
    # Pending Credit
    # -----------------------

    pending = Customer.objects.aggregate(
        total=Sum("credit_balance")
    )["total"] or Decimal("0")

    if pending > 50000:
        score -= 20

    elif pending > 20000:
        score -= 10

    # -----------------------
    # Today's Expense
    # -----------------------

    sales = Bill.objects.filter(
        created_at__date=today
    ).aggregate(
        total=Sum("final_amount")
    )["total"] or Decimal("0")

    expense = Expense.objects.filter(
        date=today
    ).aggregate(
        total=Sum("amount")
    )["total"] or Decimal("0")

    if sales > 0:

        ratio = (expense / sales) * 100

        if ratio > 50:
            score -= 20

        elif ratio > 30:
            score -= 10

    if score < 0:
        score = 0

    if score >= 90:
        status = "Excellent"
        color = "success"

    elif score >= 75:
        status = "Good"
        color = "primary"

    elif score >= 60:
        status = "Average"
        color = "warning"

    else:
        status = "Needs Attention"
        color = "danger"

    return {
        "score": score,
        "status": status,
        "color": color,
    }


from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta

from products.models import Product
from billing.models import BillItem


def get_purchase_recommendations():

    recommendations = []

    last30 = timezone.now() - timedelta(days=30)

    products = Product.objects.all()

    for product in products:

        sold = (

            BillItem.objects.filter(

                product=product,

                bill__created_at__gte=last30

            )

            .aggregate(total=Sum("quantity"))

            ["total"]

            or 0

        )

        avg_daily = sold / 30

        if avg_daily == 0:

            continue

        days_left = (

            product.quantity / avg_daily

            if avg_daily > 0 else 999

        )

        if days_left <= 7:

            recommendations.append({

                "name": product.name,

                "stock": product.quantity,

                "daily_sale": round(avg_daily, 1),

                "days_left": round(days_left, 1),

                "recommend": max(

                    int(avg_daily * 15),

                    10

                )

            })

    recommendations.sort(

        key=lambda x: x["days_left"]

    )

    return recommendations[:5]

from django.utils import timezone
from datetime import timedelta

from products.models import Product
from billing.models import BillItem


def get_dead_stock():

    dead_stock = []

    limit_date = timezone.now() - timedelta(days=90)

    products = Product.objects.all()

    for product in products:

        sold = BillItem.objects.filter(
            product=product,
            bill__created_at__gte=limit_date
        ).exists()

        if not sold and product.quantity > 0:

            dead_stock.append({

                "name": product.name,

                "stock": product.quantity,

                "purchase_price": product.purchase_price,

                "stock_value": product.quantity * product.purchase_price

            })

    dead_stock = sorted(

        dead_stock,

        key=lambda x: x["stock_value"],

        reverse=True

    )

    return dead_stock[:10]