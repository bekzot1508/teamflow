from django.contrib import admin

from .models import Workspace, WorkspaceMember


class WorkspaceMemberInline(admin.TabularInline):
    model = WorkspaceMember
    extra = 0


@admin.register(Workspace)
class WorkspaceAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "slug",
        "owner",
        "created_at",
    )
    list_filter = ("created_at",)
    search_fields = ("name", "slug", "owner__email", "owner__username")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [WorkspaceMemberInline]


@admin.register(WorkspaceMember)
class WorkspaceMemberAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "workspace",
        "user",
        "role",
        "created_at",
    )
    list_filter = ("role", "created_at")
    search_fields = (
        "workspace__name",
        "user__email",
        "user__username",
    )