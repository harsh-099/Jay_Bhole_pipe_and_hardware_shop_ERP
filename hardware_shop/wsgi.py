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


# Vercel filesystem is read-only except /tmp.
# Copy the bundled SQLite database to writable /tmp.
if os.environ.get("VERCEL"):

    source_db = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "db.sqlite3"
    )

    target_db = "/tmp/db.sqlite3"

    if os.path.exists(source_db) and not os.path.exists(target_db):
        shutil.copy2(source_db, target_db)


application = get_wsgi_application()