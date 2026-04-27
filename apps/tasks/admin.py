from django.contrib import admin

from .models import Task, TaskActivity


class TaskActivityInline(admin.TabularInline):
    model = TaskActivity
    extra = 0
    readonly_fields = (
        "actor",
        "action",
        "old_value",
        "new_value",
        "created_at",
        "updated_at",
    )
    can_delete = False


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "project",
        "status",
        "priority",
        "assignee",
        "created_by",
        "deadline",
        "is_archived",
        "created_at",
    )
    list_filter = (
        "status",
        "priority",
        "is_archived",
        "created_at",
    )
    search_fields = (
        "title",
        "description",
        "project__name",
        "assignee__email",
        "created_by__email",
    )
    list_select_related = (
        "project",
        "board",
        "column",
        "assignee",
        "created_by",
    )
    inlines = [TaskActivityInline]


@admin.register(TaskActivity)
class TaskActivityAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "task",
        "actor",
        "action",
        "created_at",
    )
    list_filter = ("action", "created_at")
    search_fields = (
        "task__title",
        "actor__email",
    )
    list_select_related = ("task", "actor")