from django.contrib import admin
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):

    list_display = (

        "user",

        "role",

        "mobile",

        "is_active",

        "created_at",

    )

    list_filter = (

        "role",

        "is_active",

    )

    search_fields = (

        "user__username",

        "mobile",

    )
