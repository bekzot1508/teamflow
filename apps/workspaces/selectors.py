from .models import Workspace, WorkspaceMember
from django.db.models import Prefetch
from apps.projects.models import Project


def get_user_workspaces(user):
    return (
        Workspace.objects
        .filter(memberships__user=user, is_archived=False)
        .select_related("owner")
        .distinct()
        .order_by("-created_at")
    )


def get_workspace_detail(*, workspace_id, user):
    return (
        Workspace.objects
        .filter(
            id=workspace_id,
            memberships__user=user,
            is_archived=False,
        )
        .select_related("owner")
        .prefetch_related(
            "memberships__user",
            Prefetch(
                "projects",
                queryset=Project.objects.filter(is_archived=False).order_by("-created_at"),
            ),
        )
        .first()
    )


def get_workspace_member(*, workspace, user):
    return WorkspaceMember.objects.filter(
        workspace=workspace,
        user=user,
    ).first()