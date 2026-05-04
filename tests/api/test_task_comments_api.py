import pytest
from rest_framework.test import APIClient

from apps.notifications.models import Notification
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
def task_comment_api_setup():
    client = APIClient()

    owner = UserFactory(username="owner", email="owner@example.com")
    mentioned = UserFactory(username="ali", email="ali@example.com")

    workspace = WorkspaceFactory(owner=owner)
    WorkspaceMemberFactory(workspace=workspace, user=owner, role=WorkspaceMember.Role.OWNER)
    WorkspaceMemberFactory(workspace=workspace, user=mentioned, role=WorkspaceMember.Role.MEMBER)

    project = ProjectFactory(workspace=workspace, created_by=owner)
    board = BoardFactory(project=project)
    column = ColumnFactory(board=board, name="Todo", position=0)

    task = TaskFactory(project=project, board=board, column=column, created_by=owner)

    client.force_authenticate(user=owner)

    return client, owner, mentioned, task


@pytest.mark.django_db
def test_task_comment_create_api(task_comment_api_setup):
    client, owner, mentioned, task = task_comment_api_setup

    response = client.post(
        f"/api/v1/tasks/{task.id}/comments/",
        {"body": "Hello team"},
        format="json",
    )

    assert response.status_code == 201
    assert response.data["success"] is True
    assert response.data["data"]["body"] == "Hello team"


@pytest.mark.django_db
def test_task_comment_mention_creates_notification_api(task_comment_api_setup):
    client, owner, mentioned, task = task_comment_api_setup

    response = client.post(
        f"/api/v1/tasks/{task.id}/comments/",
        {"body": "@ali please check this"},
        format="json",
    )

    assert response.status_code == 201
    assert Notification.objects.filter(
        recipient=mentioned,
        task=task,
        type=Notification.Type.MENTIONED,
    ).exists()


@pytest.mark.django_db
def test_non_member_cannot_comment_task_api(task_comment_api_setup):
    client, owner, mentioned, task = task_comment_api_setup

    outsider = UserFactory()
    client.force_authenticate(user=outsider)

    response = client.post(
        f"/api/v1/tasks/{task.id}/comments/",
        {"body": "I should not comment"},
        format="json",
    )

    assert response.status_code == 404