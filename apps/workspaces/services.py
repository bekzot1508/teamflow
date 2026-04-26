from django.db import transaction

from .models import Workspace, WorkspaceMember

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError

from .permissions import can_manage_workspace

User = get_user_model()


@transaction.atomic
def create_workspace(*, owner, name, description=""):
    workspace = Workspace.objects.create(
        owner=owner,
        name=name,
        description=description,
    )

    WorkspaceMember.objects.create(
        workspace=workspace,
        user=owner,
        role=WorkspaceMember.Role.OWNER,
    )

    return workspace




@transaction.atomic
def add_workspace_member(*, workspace, actor, email, role):
    if not can_manage_workspace(actor, workspace):
        raise PermissionDenied("You cannot manage this workspace.")

    user = User.objects.filter(email=email).first()

    if user is None:
        raise ValidationError("User with this email does not exist.")

    if WorkspaceMember.objects.filter(workspace=workspace, user=user).exists():
        raise ValidationError("This user is already a workspace member.")

    if role == WorkspaceMember.Role.OWNER:
        raise ValidationError("You cannot add another owner from here.")

    membership = WorkspaceMember.objects.create(
        workspace=workspace,
        user=user,
        role=role,
    )

    return membership


@transaction.atomic
def update_workspace_member_role(*, workspace, actor, membership_id, new_role):
    if not can_manage_workspace(actor, workspace):
        raise PermissionDenied("You cannot manage this workspace.")

    membership = WorkspaceMember.objects.select_for_update().get(
        id=membership_id,
        workspace=workspace,
    )

    if membership.role == WorkspaceMember.Role.OWNER:
        raise ValidationError("Workspace owner role cannot be changed.")

    if new_role == WorkspaceMember.Role.OWNER:
        raise ValidationError("Owner role cannot be assigned from here.")

    membership.role = new_role
    membership.save(update_fields=["role", "updated_at"])

    return membership


@transaction.atomic
def remove_workspace_member(*, workspace, actor, membership_id):
    if not can_manage_workspace(actor, workspace):
        raise PermissionDenied("You cannot manage this workspace.")

    membership = WorkspaceMember.objects.select_for_update().get(
        id=membership_id,
        workspace=workspace,
    )

    if membership.role == WorkspaceMember.Role.OWNER:
        raise ValidationError("Workspace owner cannot be removed.")

    if membership.user_id == actor.id:
        raise ValidationError("You cannot remove yourself from workspace management.")

    membership.delete()