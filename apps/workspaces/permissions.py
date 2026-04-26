from .models import WorkspaceMember


def get_workspace_role(user, workspace):
    membership = WorkspaceMember.objects.filter(
        workspace=workspace,
        user=user,
    ).first()

    if membership is None:
        return None

    return membership.role


def is_workspace_owner(user, workspace):
    return workspace.owner_id == user.id


def is_workspace_admin_or_owner(user, workspace):
    role = get_workspace_role(user, workspace)

    return role in [
        WorkspaceMember.Role.OWNER,
        WorkspaceMember.Role.ADMIN,
    ]


def can_manage_workspace(user, workspace):
    return is_workspace_admin_or_owner(user, workspace)


def can_create_project(user, workspace):
    return is_workspace_admin_or_owner(user, workspace)


def can_view_workspace(user, workspace):
    return WorkspaceMember.objects.filter(
        workspace=workspace,
        user=user,
    ).exists()


def can_create_task(user, workspace):
    role = get_workspace_role(user, workspace)

    return role in [
        WorkspaceMember.Role.OWNER,
        WorkspaceMember.Role.ADMIN,
        WorkspaceMember.Role.MEMBER,
    ]


def can_update_task(user, workspace):
    role = get_workspace_role(user, workspace)

    return role in [
        WorkspaceMember.Role.OWNER,
        WorkspaceMember.Role.ADMIN,
        WorkspaceMember.Role.MEMBER,
    ]


def can_only_view(user, workspace):
    return get_workspace_role(user, workspace) == WorkspaceMember.Role.VIEWER