from django.db import models

from billing.models import Bill, BillItem


class SaleReturn(models.Model):

    return_no = models.CharField(
        max_length=20,
        unique=True,
        blank=True
    )

    bill = models.ForeignKey(
        Bill,
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
        ("Partial", "Partial"),
        ("Full", "Full"),
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default="Partial"
    )

    def save(self, *args, **kwargs):

        if not self.return_no:

            last_return = SaleReturn.objects.order_by(
                "-id"
            ).first()

            if (
                last_return and
                last_return.return_no
            ):

                try:

                    last_no = int(

                        last_return.return_no.replace(
                            "SR",
                            ""
                        )

                    ) + 1

                except ValueError:

                    last_no = 1

            else:

                last_no = 1

            self.return_no = f"SR{last_no:04d}"

        super().save(
            *args,
            **kwargs
        )

    def __str__(self):

        return self.return_no


class SaleReturnItem(models.Model):

    sale_return = models.ForeignKey(
        SaleReturn,
        on_delete=models.CASCADE,
        related_name="items"
    )

    bill_item = models.ForeignKey(
        BillItem,
        on_delete=models.CASCADE
    )

    quantity = models.PositiveIntegerField()

    returned_qty = models.PositiveIntegerField(
        default=0
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    reason = models.CharField(
        max_length=100,
        default="Other"
    )

    remarks = models.TextField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    @property
    def remaining_qty(self):

        return self.bill_item.quantity - self.returned_qty

    def __str__(self):

        return self.bill_item.product.name