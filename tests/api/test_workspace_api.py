import pytest
from rest_framework.test import APIClient

from apps.workspaces.models import Workspace
from tests.factories import UserFactory, WorkspaceFactory, WorkspaceMemberFactory
from apps.workspaces.models import WorkspaceMember


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def auth_client(api_client):
    user = UserFactory(email="api@example.com")
    api_client.force_authenticate(user=user)
    return api_client, user


@pytest.mark.django_db
def test_workspace_list_api(auth_client):
    client, user = auth_client

    workspace = WorkspaceFactory(owner=user)
    WorkspaceMemberFactory(
        workspace=workspace,
        user=user,
        role=WorkspaceMember.Role.OWNER,
    )

    response = client.get("/api/v1/workspaces/")

    assert response.status_code == 200
    assert response.data["success"] is True


@pytest.mark.django_db
def test_workspace_create_api(auth_client):
    client, user = auth_client

    response = client.post(
        "/api/v1/workspaces/",
        {
            "name": "API Workspace",
            "description": "Created from test",
        },
        format="json",
    )

    assert response.status_code == 201
    assert Workspace.objects.filter(name="API Workspace").exists()


@pytest.mark.django_db
def test_workspace_detail_for_member(auth_client):
    client, user = auth_client

    workspace = WorkspaceFactory()
    WorkspaceMemberFactory(
        workspace=workspace,
        user=user,
        role=WorkspaceMember.Role.MEMBER,
    )

    response = client.get(f"/api/v1/workspaces/{workspace.id}/")

    assert response.status_code == 200


@pytest.mark.django_db
def test_workspace_detail_for_non_member_returns_404(auth_client):
    client, user = auth_client

    workspace = WorkspaceFactory()

    response = client.get(f"/api/v1/workspaces/{workspace.id}/")

    assert response.status_code == 404