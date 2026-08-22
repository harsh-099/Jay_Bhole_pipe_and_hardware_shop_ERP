from .models import ActivityLog


def log_activity(

    request,

    module,

    action,

    document_no="",

    description=""

):

    user = request.user

    role = ""

    if user.groups.exists():

        role = user.groups.first().name

    ip = request.META.get(
        "REMOTE_ADDR",
        ""
    )

    browser = request.META.get(
        "HTTP_USER_AGENT",
        ""
    )

    device = browser

    ActivityLog.objects.create(

        user=user,

        username=user.username,

        role=role,

        module=module,

        action=action,

        document_no=document_no,

        description=description,

        ip_address=ip,

        browser=browser,

        device=device,

    )   