import pytest
from rest_framework.test import APIClient

from apps.workspaces.models import WorkspaceMember
from tests.factories import UserFactory, WorkspaceFactory, WorkspaceMemberFactory


@pytest.fixture
def workspace_member_api_setup():
    client = APIClient()

    owner = UserFactory(email="owner@example.com")
    member = UserFactory(email="member@example.com")
    new_user = UserFactory(email="new@example.com")

    workspace = WorkspaceFactory(owner=owner)

    owner_membership = WorkspaceMemberFactory(
        workspace=workspace,
        user=owner,
        role=WorkspaceMember.Role.OWNER,
    )
    member_membership = WorkspaceMemberFactory(
        workspace=workspace,
        user=member,
        role=WorkspaceMember.Role.MEMBER,
    )

    client.force_authenticate(user=owner)

    return client, owner, member, new_user, workspace, owner_membership, member_membership


@pytest.mark.django_db
def test_workspace_member_add_api(workspace_member_api_setup):
    client, owner, member, new_user, workspace, owner_membership, member_membership = workspace_member_api_setup

    response = client.post(
        f"/api/v1/workspaces/{workspace.id}/members/",
        {
            "email": new_user.email,
            "role": WorkspaceMember.Role.MEMBER,
        },
        format="json",
    )

    assert response.status_code == 201
    assert WorkspaceMember.objects.filter(workspace=workspace, user=new_user).exists()


@pytest.mark.django_db
def test_workspace_member_role_update_api(workspace_member_api_setup):
    client, owner, member, new_user, workspace, owner_membership, member_membership = workspace_member_api_setup

    response = client.patch(
        f"/api/v1/workspaces/{workspace.id}/members/{member_membership.id}/",
        {"role": WorkspaceMember.Role.ADMIN},
        format="json",
    )

    member_membership.refresh_from_db()

    assert response.status_code == 200
    assert member_membership.role == WorkspaceMember.Role.ADMIN


@pytest.mark.django_db
def test_workspace_member_remove_api(workspace_member_api_setup):
    client, owner, member, new_user, workspace, owner_membership, member_membership = workspace_member_api_setup

    response = client.delete(
        f"/api/v1/workspaces/{workspace.id}/members/{member_membership.id}/",
    )

    assert response.status_code == 200
    assert not WorkspaceMember.objects.filter(id=member_membership.id).exists()


@pytest.mark.django_db
def test_workspace_owner_cannot_be_removed_api(workspace_member_api_setup):
    client, owner, member, new_user, workspace, owner_membership, member_membership = workspace_member_api_setup

    response = client.delete(
        f"/api/v1/workspaces/{workspace.id}/members/{owner_membership.id}/",
    )

    assert response.status_code == 400