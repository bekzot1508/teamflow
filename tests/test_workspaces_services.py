import pytest
from django.core.exceptions import PermissionDenied, ValidationError

from apps.workspaces.models import WorkspaceMember
from apps.workspaces.services import (
    create_workspace,
    add_workspace_member,
    update_workspace_member_role,
    remove_workspace_member,
)
from tests.factories import UserFactory, WorkspaceFactory, WorkspaceMemberFactory


@pytest.mark.django_db
def test_create_workspace_creates_owner_membership():
    owner = UserFactory()

    workspace = create_workspace(
        owner=owner,
        name="Team A",
        description="Main workspace",
    )

    membership = WorkspaceMember.objects.get(
        workspace=workspace,
        user=owner,
    )

    assert workspace.owner == owner
    assert membership.role == WorkspaceMember.Role.OWNER


@pytest.mark.django_db
def test_admin_can_add_member():
    owner = UserFactory()
    user = UserFactory(email="member@example.com")

    workspace = WorkspaceFactory(owner=owner)
    WorkspaceMemberFactory(
        workspace=workspace,
        user=owner,
        role=WorkspaceMember.Role.OWNER,
    )

    membership = add_workspace_member(
        workspace=workspace,
        actor=owner,
        email=user.email,
        role=WorkspaceMember.Role.MEMBER,
    )

    assert membership.user == user
    assert membership.role == WorkspaceMember.Role.MEMBER


@pytest.mark.django_db
def test_member_cannot_add_member():
    workspace = WorkspaceFactory()
    actor = UserFactory()
    target = UserFactory(email="target@example.com")

    WorkspaceMemberFactory(
        workspace=workspace,
        user=actor,
        role=WorkspaceMember.Role.MEMBER,
    )

    with pytest.raises(PermissionDenied):
        add_workspace_member(
            workspace=workspace,
            actor=actor,
            email=target.email,
            role=WorkspaceMember.Role.MEMBER,
        )


@pytest.mark.django_db
def test_cannot_change_owner_role():
    owner = UserFactory()
    workspace = WorkspaceFactory(owner=owner)

    owner_membership = WorkspaceMemberFactory(
        workspace=workspace,
        user=owner,
        role=WorkspaceMember.Role.OWNER,
    )

    with pytest.raises(ValidationError):
        update_workspace_member_role(
            workspace=workspace,
            actor=owner,
            membership_id=owner_membership.id,
            new_role=WorkspaceMember.Role.MEMBER,
        )


@pytest.mark.django_db
def test_cannot_remove_owner():
    owner = UserFactory()
    workspace = WorkspaceFactory(owner=owner)

    owner_membership = WorkspaceMemberFactory(
        workspace=workspace,
        user=owner,
        role=WorkspaceMember.Role.OWNER,
    )

    with pytest.raises(ValidationError):
        remove_workspace_member(
            workspace=workspace,
            actor=owner,
            membership_id=owner_membership.id,
        )