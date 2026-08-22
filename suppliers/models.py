from django.db import models


class Supplier(models.Model):

    name = models.CharField(
        max_length=200
    )

    mobile = models.CharField(
        max_length=20
    )

    address = models.TextField()

    balance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )
    ledger_balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )


    def __str__(self):

        return self.name
    
class SupplierLedger(models.Model):

    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE
    )

    date = models.DateTimeField(
        auto_now_add=True
    )

    PARTICULAR = (
        ("Purchase", "Purchase"),
        ("Purchase Return", "Purchase Return"),
        ("Payment", "Payment"),
    )

    particular = models.CharField(
        max_length=30,
        choices=PARTICULAR
    )

    debit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    credit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    balance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    remarks = models.CharField(
        max_length=200,
        blank=True
    )

    def __str__(self):
        return self.supplier.name