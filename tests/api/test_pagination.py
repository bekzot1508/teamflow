import pytest
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
from rest_framework.test import APIClient

@pytest.mark.django_db
def test_task_pagination():
    user = UserFactory()
    client = APIClient()
    client.force_authenticate(user=user)

    workspace = WorkspaceFactory(owner=user)
    WorkspaceMemberFactory(
        workspace=workspace,
        user=user,
        role=WorkspaceMember.Role.OWNER,
    )

    project = ProjectFactory(workspace=workspace, created_by=user)
    board = BoardFactory(project=project)
    column = ColumnFactory(board=board)

    for _ in range(30):
        TaskFactory(
            project=project,
            board=board,
            column=column,
            created_by=user,
        )

    response = client.get(f"/api/v1/tasks/?project_id={project.id}")

    assert response.status_code == 200
    assert response.data["success"] is True
    assert "results" in response.data["data"]
    assert response.data["data"]["count"] == 30
    assert len(response.data["data"]["results"]) == 10