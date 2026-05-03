import pytest

from apps.tasks.selectors import get_project_tasks
from apps.workspaces.selectors import get_user_workspaces
from apps.projects.selectors import get_user_projects
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


@pytest.mark.django_db
def test_get_user_workspaces_only_returns_member_workspaces():
    user = UserFactory()

    workspace_1 = WorkspaceFactory()
    workspace_2 = WorkspaceFactory()

    WorkspaceMemberFactory(
        workspace=workspace_1,
        user=user,
        role=WorkspaceMember.Role.MEMBER,
    )

    result = get_user_workspaces(user)

    assert workspace_1 in list(result)
    assert workspace_2 not in list(result)


@pytest.mark.django_db
def test_get_user_projects_only_returns_member_projects():
    user = UserFactory()

    workspace_1 = WorkspaceFactory()
    workspace_2 = WorkspaceFactory()

    WorkspaceMemberFactory(
        workspace=workspace_1,
        user=user,
        role=WorkspaceMember.Role.MEMBER,
    )

    project_1 = ProjectFactory(workspace=workspace_1)
    project_2 = ProjectFactory(workspace=workspace_2)

    result = get_user_projects(user)

    assert project_1 in list(result)
    assert project_2 not in list(result)


@pytest.mark.django_db
def test_get_project_tasks_excludes_archived_tasks():
    owner = UserFactory()
    workspace = WorkspaceFactory(owner=owner)
    WorkspaceMemberFactory(workspace=workspace, user=owner, role=WorkspaceMember.Role.OWNER)

    project = ProjectFactory(workspace=workspace, created_by=owner)
    board = BoardFactory(project=project)
    column = ColumnFactory(board=board)

    active_task = TaskFactory(project=project, board=board, column=column, created_by=owner)
    archived_task = TaskFactory(
        project=project,
        board=board,
        column=column,
        created_by=owner,
        is_archived=True,
    )

    result = get_project_tasks(project=project)

    assert active_task in list(result)
    assert archived_task not in list(result)