from django.db import models
from suppliers.models import Supplier
from products.models import Product


class Purchase(models.Model):

    PAYMENT = [
        ("Cash", "Cash"),
        ("UPI", "UPI"),
        ("Credit", "Credit"),
    ]

    purchase_no = models.CharField(
        max_length=20,
        unique=True
    )

    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE
    )

    supplier_invoice_no = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    discount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    discount_amount = models.DecimalField(
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
        default="Cash"
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


    remarks = models.TextField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.purchase_no


class PurchaseItem(models.Model):

    purchase = models.ForeignKey(
        Purchase,
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
        decimal_places=2
    )

    total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    def __str__(self):
        return self.product.name