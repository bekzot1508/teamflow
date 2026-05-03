import pytest
from rest_framework.test import APIClient

from apps.tasks.models import Task
from apps.workspaces.models import WorkspaceMember
from tests.factories import (
    UserFactory,
    WorkspaceFactory,
    WorkspaceMemberFactory,
    ProjectFactory,
    BoardFactory,
    ColumnFactory,
)


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def setup_project():
    owner = UserFactory()
    assignee = UserFactory()

    workspace = WorkspaceFactory(owner=owner)
    WorkspaceMemberFactory(
        workspace=workspace,
        user=owner,
        role=WorkspaceMember.Role.OWNER,
    )
    WorkspaceMemberFactory(
        workspace=workspace,
        user=assignee,
        role=WorkspaceMember.Role.MEMBER,
    )

    project = ProjectFactory(workspace=workspace, created_by=owner)
    board = BoardFactory(project=project)
    column = ColumnFactory(board=board, name="Todo", position=0)

    return owner, assignee, workspace, project, board, column


@pytest.mark.django_db
def test_task_create_api(api_client, setup_project):
    owner, assignee, workspace, project, board, column = setup_project

    api_client.force_authenticate(user=owner)

    response = api_client.post(
        "/api/v1/tasks/",
        {
            "project_id": project.id,
            "title": "API Task",
            "description": "Task created by API",
            "priority": "high",
            "assignee_id": assignee.id,
        },
        format="json",
    )

    assert response.status_code == 201
    assert Task.objects.filter(title="API Task").exists()


@pytest.mark.django_db
def test_task_list_api(api_client, setup_project):
    owner, assignee, workspace, project, board, column = setup_project

    Task.objects.create(
        project=project,
        board=board,
        column=column,
        title="List task",
        created_by=owner,
        assignee=assignee,
    )

    api_client.force_authenticate(user=owner)

    response = api_client.get(f"/api/v1/tasks/?project_id={project.id}")

    assert response.status_code == 200
    assert response.data["success"] is True


@pytest.mark.django_db
def test_viewer_cannot_create_task_api(api_client, setup_project):
    owner, assignee, workspace, project, board, column = setup_project

    viewer = UserFactory()
    WorkspaceMemberFactory(
        workspace=workspace,
        user=viewer,
        role=WorkspaceMember.Role.VIEWER,
    )

    api_client.force_authenticate(user=viewer)

    response = api_client.post(
        "/api/v1/tasks/",
        {
            "project_id": project.id,
            "title": "Forbidden",
            "priority": "medium",
        },
        format="json",
    )

    # assert response.status_code in [403, 500]
    assert response.status_code == 403


