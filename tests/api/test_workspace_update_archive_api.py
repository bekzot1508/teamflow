import pytest
from rest_framework.test import APIClient

from apps.workspaces.models import WorkspaceMember
from tests.factories import UserFactory, WorkspaceFactory, WorkspaceMemberFactory


@pytest.fixture
def auth_client():
    client = APIClient()
    user = UserFactory()
    client.force_authenticate(user=user)
    return client, user


@pytest.mark.django_db
def test_workspace_update_api(auth_client):
    client, user = auth_client

    workspace = WorkspaceFactory(owner=user)
    WorkspaceMemberFactory(
        workspace=workspace,
        user=user,
        role=WorkspaceMember.Role.OWNER,
    )

    response = client.patch(
        f"/api/v1/workspaces/{workspace.id}/",
        {
            "name": "Updated Workspace",
            "description": "Updated description",
        },
        format="json",
    )

    workspace.refresh_from_db()

    assert response.status_code == 200
    assert workspace.name == "Updated Workspace"


@pytest.mark.django_db
def test_workspace_archive_api(auth_client):
    client, user = auth_client

    workspace = WorkspaceFactory(owner=user)
    WorkspaceMemberFactory(
        workspace=workspace,
        user=user,
        role=WorkspaceMember.Role.OWNER,
    )

    response = client.post(f"/api/v1/workspaces/{workspace.id}/archive/")

    workspace.refresh_from_db()

    assert response.status_code == 200
    assert workspace.is_archived is True


@pytest.mark.django_db
def test_non_owner_cannot_archive_workspace_api(auth_client):
    client, user = auth_client

    owner = UserFactory()
    workspace = WorkspaceFactory(owner=owner)

    WorkspaceMemberFactory(
        workspace=workspace,
        user=owner,
        role=WorkspaceMember.Role.OWNER,
    )
    WorkspaceMemberFactory(
        workspace=workspace,
        user=user,
        role=WorkspaceMember.Role.ADMIN,
    )

    response = client.post(f"/api/v1/workspaces/{workspace.id}/archive/")

    assert response.status_code == 403