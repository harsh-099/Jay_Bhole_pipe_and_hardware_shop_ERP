from django.db import models


class ShopSettings(models.Model):

    shop_name = models.CharField(
        max_length=200
    )

    owner_name = models.CharField(
        max_length=200,
        blank=True
    )

    mobile = models.CharField(
        max_length=15,
        blank=True
    )

    address = models.TextField(
        blank=True
    )

    gst_number = models.CharField(
        max_length=30,
        blank=True
    )
    upi_id = models.CharField(
    max_length=100,
    blank=True
    )

    logo = models.ImageField(
        upload_to='logo/',
        blank=True,
        null=True
    )

    def __str__(self):

        return self.shop_name