from advisor.utils import (
    get_dead_stock,
    get_purchase_recommendations,
)

from products.models import Product
from customers.models import Customer
from django.db.models import Sum


def global_notifications(request):

    notifications = []

    # ---------------- Low Stock ----------------

    low_stock = Product.objects.filter(
        quantity__lte=10
    ).count()

    if low_stock:

        notifications.append({

            "title": "Low Stock",

            "message": f"{low_stock} Products Running Low",

            "icon": "fa-box",

            "color": "warning",

            "url": "/reports/low-stock/"

        })

    # ---------------- Dead Stock ----------------

    dead_stock = get_dead_stock()

    if dead_stock:

        notifications.append({

            "title": "Dead Stock",

            "message": f"{len(dead_stock)} Products Not Sold",

            "icon": "fa-box-open",

            "color": "danger",

            "url": "/reports/dead-stock/"

        })

    # ---------------- Recovery ----------------

    pending = Customer.objects.aggregate(

        total=Sum("credit_balance")

    )["total"] or 0

    if pending > 0:

        notifications.append({

            "title": "Payment Recovery",

            "message": f"₹{pending} Pending",

            "icon": "fa-money-bill-wave",

            "color": "primary",

            "url": "/reports/payment-recovery/"

        })

    # ---------------- Purchase Advice ----------------

    purchase = get_purchase_recommendations()

    if purchase:

        notifications.append({

            "title": "Purchase Suggestions",

            "message": f"{len(purchase)} Products Need Purchase",

            "icon": "fa-cart-shopping",

            "color": "success",

            "url": "/reports/purchase/"

        })

    return {

        "notifications": notifications,

        "notification_count": len(notifications)

    }