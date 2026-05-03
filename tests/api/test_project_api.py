import pytest
from rest_framework.test import APIClient

from apps.projects.models import Project
from apps.workspaces.models import WorkspaceMember
from tests.factories import UserFactory, WorkspaceFactory, WorkspaceMemberFactory, ProjectFactory


@pytest.fixture
def client_user():
    client = APIClient()
    user = UserFactory()
    client.force_authenticate(user=user)
    return client, user


@pytest.mark.django_db
def test_project_list_api(client_user):
    client, user = client_user

    workspace = WorkspaceFactory(owner=user)
    WorkspaceMemberFactory(workspace=workspace, user=user, role=WorkspaceMember.Role.OWNER)

    ProjectFactory(workspace=workspace, created_by=user)

    response = client.get("/api/v1/projects/")

    assert response.status_code == 200
    assert response.data["success"] is True


@pytest.mark.django_db
def test_project_create_api(client_user):
    client, user = client_user

    workspace = WorkspaceFactory(owner=user)
    WorkspaceMemberFactory(workspace=workspace, user=user, role=WorkspaceMember.Role.OWNER)

    response = client.post(
        "/api/v1/projects/",
        {
            "workspace_id": workspace.id,
            "name": "API Project",
            "description": "Created from API",
        },
        format="json",
    )

    assert response.status_code == 201
    assert Project.objects.filter(name="API Project").exists()


@pytest.mark.django_db
def test_viewer_cannot_create_project_api(client_user):
    client, user = client_user

    workspace = WorkspaceFactory()
    WorkspaceMemberFactory(workspace=workspace, user=user, role=WorkspaceMember.Role.VIEWER)

    response = client.post(
        "/api/v1/projects/",
        {
            "workspace_id": workspace.id,
            "name": "Forbidden Project",
        },
        format="json",
    )

    assert response.status_code == 403


@pytest.mark.django_db
def test_project_archive_api(client_user):
    client, user = client_user

    workspace = WorkspaceFactory(owner=user)
    WorkspaceMemberFactory(workspace=workspace, user=user, role=WorkspaceMember.Role.OWNER)

    project = ProjectFactory(workspace=workspace, created_by=user)

    response = client.post(f"/api/v1/projects/{project.id}/archive/")

    project.refresh_from_db()

    assert response.status_code == 200
    assert project.is_archived is True