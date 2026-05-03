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
    TaskFactory,
)


@pytest.fixture
def task_api_setup():
    client = APIClient()

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

    task = TaskFactory(
        project=project,
        board=board,
        column=column,
        created_by=owner,
        assignee=assignee,
        status=Task.Status.TODO,
    )

    client.force_authenticate(user=owner)

    return client, owner, assignee, task


@pytest.mark.django_db
def test_task_update_api(task_api_setup):
    client, owner, assignee, task = task_api_setup

    response = client.put(
        f"/api/v1/tasks/{task.id}/update/",
        {
            "title": "Updated Task",
            "description": "Updated desc",
            "priority": "high",
            "assignee_id": assignee.id,
        },
        format="json",
    )

    task.refresh_from_db()

    assert response.status_code == 200
    assert task.title == "Updated Task"
    assert task.priority == "high"


@pytest.mark.django_db
def test_task_archive_api(task_api_setup):
    client, owner, assignee, task = task_api_setup

    response = client.post(f"/api/v1/tasks/{task.id}/archive/")

    task.refresh_from_db()

    assert response.status_code == 200
    assert task.is_archived is True