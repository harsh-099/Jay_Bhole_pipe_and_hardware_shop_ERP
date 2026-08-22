from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps


def allowed_roles(roles=[]):

    def decorator(view_func):

        @wraps(view_func)
        def wrapper(request, *args, **kwargs):

            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)

            if request.user.groups.filter(name__in=roles).exists():
                return view_func(request, *args, **kwargs)

            messages.error(
                request,
                "Access Denied!"
            )

            return redirect("login")

        return wrapper

    return decorator