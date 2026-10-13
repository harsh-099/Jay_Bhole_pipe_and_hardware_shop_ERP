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

    return {
        "notifications": notifications,
        "notification_count": len(notifications)
    }