from dataclasses import dataclass

from django.db.models import Q

from .models import Task


@dataclass
class TaskFilters:
    status: str | None = None
    priority: str | None = None
    assignee_id: int | None = None
    deadline_before: str | None = None
    deadline_after: str | None = None
    search: str | None = None


def get_project_tasks(*, project, filters: TaskFilters | None = None):
    qs = (
        Task.objects
        .filter(project=project, is_archived=False)
        .select_related(
            "project",
            "board",
            "column",
            "assignee",
            "created_by",
        )
        .order_by("column__position", "position", "-created_at")
    )

    if filters is None:
        return qs

    if filters.status:
        qs = qs.filter(status=filters.status)

    if filters.priority:
        qs = qs.filter(priority=filters.priority)

    if filters.assignee_id:
        qs = qs.filter(assignee_id=filters.assignee_id)

    if filters.deadline_before:
        qs = qs.filter(deadline__lte=filters.deadline_before)

    if filters.deadline_after:
        qs = qs.filter(deadline__gte=filters.deadline_after)

    if filters.search:
        qs = qs.filter(
            Q(title__icontains=filters.search) |
            Q(description__icontains=filters.search)
        )

    return qs


def get_task_detail(*, task_id, user):
    return (
        Task.objects
        .filter(
            id=task_id,
            project__workspace__memberships__user=user,
        )
        .select_related(
            "project",
            "project__workspace",
            "board",
            "column",
            "assignee",
            "created_by",
        )
        .prefetch_related(
            "activities__actor",
        )
        .first()
    )


def get_next_task_position(*, column):
    last_task = (
        Task.objects
        .filter(column=column)
        .order_by("-position")
        .first()
    )

    if last_task is None:
        return 0

    return last_task.position + 1