from django.db import models
from suppliers.models import Supplier
from products.models import Product


class PurchaseOrder(models.Model):

    STATUS = [

        ("Pending", "Pending"),
        ("Ordered", "Ordered"),
        ("Received", "Received"),
        ("Cancelled", "Cancelled"),

    ]

    PAYMENT = [

        ("Cash", "Cash"),
        ("UPI", "UPI"),
        ("Credit", "Credit"),

    ]

    po_no = models.CharField(
        max_length=20,
        unique=True
    )

    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE
    )

    order_date = models.DateField(
        auto_now_add=True
    )

    expected_delivery = models.DateField(
        blank=True,
        null=True
    )

    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    discount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    final_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT,
        default="Credit"
    )

    paid_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    balance_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default="Pending"
    )

    remarks = models.TextField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return self.po_no


class PurchaseOrderItem(models.Model):

    purchase_order = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.CASCADE,
        related_name="items"
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    quantity = models.PositiveIntegerField()

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    def __str__(self):

        return f"{self.purchase_order.po_no} - {self.product.name}"