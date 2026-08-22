from django.db import models


class Expense(models.Model):

    category = models.CharField(
        max_length=100
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    description = models.TextField(
        blank=True
    )

    date = models.DateField(
        auto_now_add=True
    )

    def __str__(self):

        return self.category