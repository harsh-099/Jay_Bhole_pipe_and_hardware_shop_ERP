from django.db import models
from purchases.models import Purchase, PurchaseItem
from suppliers.models import Supplier

class PurchaseReturn(models.Model):

    return_no = models.CharField(
        max_length=20,
        blank=True,
        default=""
    )

    purchase = models.ForeignKey(
        Purchase,
        on_delete=models.CASCADE
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    total_return = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    STATUS = (
        ('Partial', 'Partial'),
        ('Full', 'Full'),
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default='Partial'
    )

    def __str__(self):

        return self.return_no


class PurchaseReturnItem(models.Model):

    purchase_return = models.ForeignKey(
        PurchaseReturn,
        on_delete=models.CASCADE,
        related_name='items'
    )

    purchase_item = models.ForeignKey(
        PurchaseItem,
        on_delete=models.CASCADE
    )

    quantity = models.PositiveIntegerField()

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    reason = models.CharField(
        max_length=100,
        default='Other'
    )

    remarks = models.TextField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )
    supplier = models.ForeignKey(
    Supplier,
    on_delete=models.CASCADE,
    null=True
)

    def __str__(self):

        return self.purchase_item.product.name