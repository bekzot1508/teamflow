from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    model = User

    list_display = (
        "id",
        "email",
        "username",
        "full_name",
        "is_staff",
        "is_active",
        "created_at",
    )

    list_filter = (
        "is_staff",
        "is_active",
    )

    search_fields = (
        "email",
        "username",
        "full_name",
    )

    ordering = ("-created_at",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal Info", {"fields": ("username", "full_name", "avatar")}),
        ("Permissions", {"fields": ("is_staff", "is_active", "is_superuser")}),
        ("Important Dates", {"fields": ("last_login",)}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "email",
                "username",
                "full_name",
                "password1",
                "password2",
                "is_staff",
                "is_active",
            ),
        }),
    )