from django.contrib import admin
from .models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "workspace", "created_by", "created_at")
    search_fields = ("name", "workspace__name")
    list_filter = ("created_at",)