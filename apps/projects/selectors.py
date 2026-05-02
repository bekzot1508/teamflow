from .models import Project


def get_project_detail(*, project_id, user):
    return (
        Project.objects
        .filter(
            id=project_id,
            workspace__memberships__user=user,
            is_archived=False,
        )
        .select_related(
            "workspace",
            "created_by",
        )
        .prefetch_related(
            "boards__columns",
            "tasks__assignee",
        )
        .first()
    )


def get_user_projects(user):
    return (
        Project.objects
        .filter(
            workspace__memberships__user=user,
            is_archived=False,
        )
        .select_related(
            "workspace",
            "created_by",
        )
        .order_by("-created_at")
        .distinct()
    )