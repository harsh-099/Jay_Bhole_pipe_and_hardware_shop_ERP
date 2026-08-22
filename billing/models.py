from django.db import models
from customers.models import Customer
from products.models import Product


class Bill(models.Model):

    PAYMENT_CHOICES = [

        ("Cash", "Cash"),

        ("UPI", "UPI"),

        ("Credit", "Credit"),

    ]

    DISCOUNT_CHOICES = [

        ("Amount", "Amount"),

        ("Percent", "Percent"),

    ]

    invoice_no = models.CharField(
        max_length=20,
        unique=True
    )

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_CHOICES,
        default="Cash"
    )

    paid_amount = models.DecimalField(
    max_digits=10,
    decimal_places=2,
    default=0
    )

    balance_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    STATUS = (
        ("Pending", "Pending"),
        ("Partial", "Partial"),
        ("Paid", "Paid"),
    )

    payment_status = models.CharField(
        max_length=20,
        choices=STATUS,
        default="Paid"
    )

    # -----------------------
    # Amounts
    # -----------------------

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    discount_type = models.CharField(
        max_length=10,
        choices=DISCOUNT_CHOICES,
        default="Amount"
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
        max_digits=10,
        decimal_places=2,
        default=0
    )

    cash_amount = models.DecimalField(
    max_digits=10,
    decimal_places=2,
    default=0
    )

    upi_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    credit_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    change_amount = models.DecimalField(
    max_digits=10,
    decimal_places=2,
    default=0
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    

    def __str__(self):

        return self.invoice_no


class BillItem(models.Model):

    bill = models.ForeignKey(
        Bill,
        on_delete=models.CASCADE,
        related_name="items"
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    quantity = models.PositiveIntegerField(
        default=1
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    purchase_price = models.DecimalField(
    max_digits=10,
    decimal_places=2,
    default=0
    )

    total = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    def __str__(self):

        return f"{self.bill.invoice_no} - {self.product.name}"