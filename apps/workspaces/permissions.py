from .models import WorkspaceMember


def is_workspace_owner(user, workspace):
    return workspace.owner_id == user.id


def can_manage_workspace(user, workspace):
    if is_workspace_owner(user, workspace):
        return True

    return WorkspaceMember.objects.filter(
        workspace=workspace,
        user=user,
        role__in=[
            WorkspaceMember.Role.OWNER,
            WorkspaceMember.Role.ADMIN,
        ],
    ).exists()


def can_view_workspace(user, workspace):
    return WorkspaceMember.objects.filter(
        workspace=workspace,
        user=user,
    ).exists()