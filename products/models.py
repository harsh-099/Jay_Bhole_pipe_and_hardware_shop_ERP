from django.db import models
from django.core.exceptions import ValidationError


class Product(models.Model):

    name = models.CharField(
        max_length=200,
        unique=True
    )

    category = models.CharField(max_length=100)

    purchase_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    selling_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    quantity = models.IntegerField(default=0)

    unit = models.CharField(max_length=50)

    def clean(self):

        name = self.name.strip().lower()

        qs = Product.objects.filter(
            name__iexact=name
        )

        if self.pk:
            qs = qs.exclude(pk=self.pk)

        if qs.exists():
            raise ValidationError({
                "name": "This product already exists."
            })

    def save(self, *args, **kwargs):

        self.name = self.name.strip()

        self.full_clean()

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name