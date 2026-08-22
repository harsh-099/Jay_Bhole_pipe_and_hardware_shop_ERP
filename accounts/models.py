from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):

    ROLE_CHOICES = (

        ("Admin", "Admin"),

        ("Manager", "Manager"),

        ("Cashier", "Cashier"),

        ("Store", "Store Staff"),

        ("Accountant", "Accountant"),

    )

    user = models.OneToOneField(

        User,

        on_delete=models.CASCADE,

        related_name="profile"

    )

    role = models.CharField(

        max_length=20,

        choices=ROLE_CHOICES,

        default="Cashier"

    )

    mobile = models.CharField(

        max_length=15,

        blank=True

    )

    email = models.EmailField(

        blank=True

    )

    address = models.TextField(

        blank=True

    )

    photo = models.ImageField(

        upload_to="users/",

        blank=True,

        null=True

    )

    is_active = models.BooleanField(

        default=True

    )

    created_at = models.DateTimeField(

        auto_now_add=True

    )

    updated_at = models.DateTimeField(

        auto_now=True

    )

    def __str__(self):

        return f"{self.user.username} ({self.role})"


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):

    if created:

        UserProfile.objects.create(

            user=instance

        )


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):

    instance.profile.save()
