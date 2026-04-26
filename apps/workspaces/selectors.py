from .models import Workspace, WorkspaceMember


def get_user_workspaces(user):
    return (
        Workspace.objects
        .filter(memberships__user=user)
        .select_related("owner")
        .distinct()
        .order_by("-created_at")
    )


def get_workspace_detail(*, workspace_id, user):
    return (
        Workspace.objects
        .filter(id=workspace_id, memberships__user=user)
        .select_related("owner")
        .prefetch_related("memberships__user")
        .first()
    )


def get_workspace_member(*, workspace, user):
    return WorkspaceMember.objects.filter(
        workspace=workspace,
        user=user,
    ).first()