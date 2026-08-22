from django.http import FileResponse
from django.conf import settings
import os
import shutil
from django.shortcuts import render, redirect
from django.contrib import messages
from accounts.decorators import allowed_roles

@allowed_roles(["Admin"])
def backup_database(request):

    db_path = os.path.join(
        settings.BASE_DIR,
        'db.sqlite3'
    )

    return FileResponse(
        open(db_path, 'rb'),
        as_attachment=True,
        filename='hardware_shop_backup.sqlite3'
    )




@allowed_roles(["Admin"])
def restore_database(request):

    if request.method == "POST":

        uploaded_file = request.FILES.get("backup_file")

        if uploaded_file:

            # Only SQLite backup allowed
            if not uploaded_file.name.endswith(".sqlite3"):

                messages.error(
                    request,
                    "Please upload a valid SQLite Backup File."
                )

                return redirect("restore_database")

            db_path = settings.BASE_DIR / "db.sqlite3"

            temp_path = settings.BASE_DIR / "restore.sqlite3"

            # Save uploaded file temporarily
            with open(temp_path, "wb+") as destination:

                for chunk in uploaded_file.chunks():

                    destination.write(chunk)

            # Replace Database
            shutil.copy(temp_path, db_path)

            os.remove(temp_path)

            messages.success(
                request,
                "Database Restored Successfully. Please Restart the Server."
            )

            return redirect("/")

    return render(
        request,
        "backup/restore.html"
    )