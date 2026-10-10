
import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create a demo admin user if it does not exist."

    def handle(self, *args, **options):
        User = get_user_model()

        username = os.environ.get("DEMO_ADMIN_USERNAME", "Harshnil@123")
        password = os.environ.get("DEMO_ADMIN_PASSWORD")

        if not password:
            self.stderr.write(
                self.style.ERROR(
                    "DEMO_ADMIN_PASSWORD environment variable is required."
                )
            )
            return

        user = User.objects.filter(username=username).first()

        if user:
            self.stdout.write(
                self.style.WARNING(
                    f"User '{username}' already exists. No changes made."
                )
            )
            return

        user = User.objects.create_superuser(
            username=username,
            email="",
            password=password,
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Superuser '{user.username}' created successfully."
            )
        )
