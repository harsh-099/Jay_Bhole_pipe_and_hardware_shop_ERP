import json
import subprocess
import sys
import tempfile
import os

from django.conf import settings
from django.core.management import call_command
from django.http import FileResponse
from django.shortcuts import render, redirect
from django.contrib import messages

from accounts.decorators import allowed_roles


@allowed_roles(["Admin"])
def backup_database(request):

    try:
        temp_file = tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".json",
            encoding="utf-8",
            delete=False
        )

        temp_path = temp_file.name
        temp_file.close()

        with open(temp_path, "w", encoding="utf-8") as output:
            call_command(
                "dumpdata",
                exclude=[
                    "contenttypes",
                    "auth.permission",
                ],
                indent=2,
                stdout=output,
            )

        response = FileResponse(
            open(temp_path, "rb"),
            as_attachment=True,
            filename="hardware_shop_backup.json",
            content_type="application/json",
        )

        response["Content-Disposition"] = (
            'attachment; filename="hardware_shop_backup.json"'
        )

        return response

    except Exception as e:
        messages.error(
            request,
            f"Backup failed: {str(e)}"
        )
        return redirect("/")


@allowed_roles(["Admin"])
def restore_database(request):

    if request.method == "POST":

        uploaded_file = request.FILES.get("backup_file")

        if not uploaded_file:
            messages.error(request, "Please select a backup file.")
            return redirect("restore_database")

        if not uploaded_file.name.lower().endswith(".json"):
            messages.error(
                request,
                "Please upload a valid JSON backup file."
            )
            return redirect("restore_database")

        temp_path = None

        try:
            with tempfile.NamedTemporaryFile(
                suffix=".json",
                delete=False
            ) as temp_file:
                temp_path = temp_file.name

                for chunk in uploaded_file.chunks():
                    temp_file.write(chunk)

            # Validate JSON before attempting restore.
            with open(temp_path, "r", encoding="utf-8") as source:
                json.load(source)

            # Restore records into the currently configured database.
            call_command("loaddata", temp_path)

            messages.success(
                request,
                "Database backup restored successfully."
            )

        except Exception as e:
            messages.error(
                request,
                f"Restore failed: {str(e)}"
            )

        finally:
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)

        return redirect("restore_database")

    return render(request, "backup/restore.html")