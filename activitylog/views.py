from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from datetime import date

from accounts.decorators import allowed_roles
from .models import ActivityLog


@login_required
@allowed_roles(["Admin", "Manager"])
def activity_logs(request):

    logs = ActivityLog.objects.all()

    module = request.GET.get("module")

    user = request.GET.get("user")

    if module:
        logs = logs.filter(module=module)

    if user:
        logs = logs.filter(username=user)

    total_logs = ActivityLog.objects.count()

    today_logs = ActivityLog.objects.filter(
        created_at__date=date.today()
    ).count()

    login_logs = ActivityLog.objects.filter(
        action__icontains="Login"
    ).count()

    invoice_logs = ActivityLog.objects.filter(
        module="Billing"
    ).count()

    modules = ActivityLog.objects.values_list(
        "module",
        flat=True
    ).distinct()

    users = ActivityLog.objects.values_list(
        "username",
        flat=True
    ).distinct()

    return render(
        request,
        "activitylog/list.html",
        {
            "logs": logs,
            "modules": modules,
            "users": users,
            "total_logs": total_logs,
            "today_logs": today_logs,
            "login_logs": login_logs,
            "invoice_logs": invoice_logs,
        },
    )