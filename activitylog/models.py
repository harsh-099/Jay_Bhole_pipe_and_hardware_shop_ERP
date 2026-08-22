from django.db import models
from django.contrib.auth.models import User


class ActivityLog(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    username = models.CharField(
        max_length=100
    )

    role = models.CharField(
        max_length=100,
        blank=True
    )

    module = models.CharField(
        max_length=100
    )

    action = models.CharField(
        max_length=200
    )

    document_no = models.CharField(
        max_length=100,
        blank=True
    )

    description = models.TextField(
        blank=True
    )

    ip_address = models.CharField(
        max_length=50,
        blank=True
    )

    browser = models.CharField(
        max_length=200,
        blank=True
    )

    device = models.CharField(
        max_length=200,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:

        ordering = ["-created_at"]

        verbose_name = "Activity Log"

        verbose_name_plural = "Activity Logs"

    def __str__(self):

        return f"{self.username} - {self.action}"