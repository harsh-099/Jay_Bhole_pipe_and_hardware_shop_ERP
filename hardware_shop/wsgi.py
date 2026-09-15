"""
WSGI config for hardware_shop project.
"""

import os
import shutil

from django.core.wsgi import get_wsgi_application


os.environ.setdefault(
    'DJANGO_SETTINGS_MODULE',
    'hardware_shop.settings'
)


# ---------------------------------------------------------
# VERCEL SQLITE DATABASE
# ---------------------------------------------------------
# Vercel filesystem is read-only except /tmp.
# Copy bundled SQLite database to writable /tmp.
# ---------------------------------------------------------

if os.environ.get("VERCEL"):

    source_db = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "db.sqlite3"
    )

    target_db = "/tmp/db.sqlite3"

    if os.path.exists(source_db) and not os.path.exists(target_db):
        shutil.copy2(source_db, target_db)


# ---------------------------------------------------------
# START DJANGO
# ---------------------------------------------------------

application = get_wsgi_application()


# ---------------------------------------------------------
# AUTOMATIC SUPERUSER FOR VERCEL
# ---------------------------------------------------------

if os.environ.get("VERCEL"):

    try:

        from django.contrib.auth import get_user_model

        User = get_user_model()

        username = os.environ.get(
            "DJANGO_SUPERUSER_USERNAME",
            "admin"
        )

        password = os.environ.get(
            "DJANGO_SUPERUSER_PASSWORD"
        )

        email = os.environ.get(
            "DJANGO_SUPERUSER_EMAIL",
            "admin@example.com"
        )

        if password:

            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "email": email,
                    "is_staff": True,
                    "is_superuser": True,
                    "is_active": True,
                }
            )

            if created:

                user.set_password(password)

                user.is_staff = True
                user.is_superuser = True
                user.is_active = True

                user.save()

            else:

                # Make sure existing user is also superuser
                changed = False

                if not user.is_staff:
                    user.is_staff = True
                    changed = True

                if not user.is_superuser:
                    user.is_superuser = True
                    changed = True

                if not user.is_active:
                    user.is_active = True
                    changed = True

                if changed:
                    user.save()

    except Exception as e:

        print(
            "Superuser setup error:",
            e
        )