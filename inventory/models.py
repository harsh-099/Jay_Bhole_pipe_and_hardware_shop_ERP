from django.db import models
from products.models import Product


class StockLedger(models.Model):

    TRANSACTION_TYPES = (

        ('IN', 'Stock In'),
        ('OUT', 'Stock Out'),

    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    transaction_type = models.CharField(
        max_length=10,
        choices=TRANSACTION_TYPES
    )

    quantity = models.IntegerField()

    remarks = models.CharField(
        max_length=200,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return f"{self.product.name} - {self.transaction_type}"