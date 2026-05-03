import pytest
from django.core.exceptions import PermissionDenied, ValidationError

from apps.projects.models import Column
from apps.tasks.models import Task, TaskActivity
from apps.tasks.services import create_task, update_task, archive_task
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
def test_create_task_success():
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

    task = create_task(
        project=project,
        board=board,
        column=column,
        actor=owner,
        title="Build auth",
        description="Implement auth",
        assignee=assignee,
    )

    assert task.title == "Build auth"
    assert task.assignee == assignee
    assert TaskActivity.objects.filter(
        task=task,
        action=TaskActivity.Action.TASK_CREATED,
    ).exists()


@pytest.mark.django_db
def test_viewer_cannot_create_task():
    viewer = UserFactory()
    workspace = WorkspaceFactory()
    WorkspaceMemberFactory(
        workspace=workspace,
        user=viewer,
        role=WorkspaceMember.Role.VIEWER,
    )

    project = ProjectFactory(workspace=workspace, created_by=viewer)
    board = BoardFactory(project=project)
    column = ColumnFactory(board=board)

    with pytest.raises(PermissionDenied):
        create_task(
            project=project,
            board=board,
            column=column,
            actor=viewer,
            title="Forbidden task",
        )


@pytest.mark.django_db
def test_assignee_must_be_workspace_member():
    owner = UserFactory()
    outsider = UserFactory()
    workspace = WorkspaceFactory(owner=owner)

    WorkspaceMemberFactory(
        workspace=workspace,
        user=owner,
        role=WorkspaceMember.Role.OWNER,
    )

    project = ProjectFactory(workspace=workspace, created_by=owner)
    board = BoardFactory(project=project)
    column = ColumnFactory(board=board)

    with pytest.raises(ValidationError):
        create_task(
            project=project,
            board=board,
            column=column,
            actor=owner,
            title="Invalid assignee",
            assignee=outsider,
        )


@pytest.mark.django_db
def test_update_task_logs_assignee_change():
    owner = UserFactory()
    old_assignee = UserFactory()
    new_assignee = UserFactory()

    workspace = WorkspaceFactory(owner=owner)

    for user in [owner, old_assignee, new_assignee]:
        WorkspaceMemberFactory(
            workspace=workspace,
            user=user,
            role=WorkspaceMember.Role.MEMBER,
        )

    WorkspaceMember.objects.filter(workspace=workspace, user=owner).update(
        role=WorkspaceMember.Role.OWNER
    )

    project = ProjectFactory(workspace=workspace, created_by=owner)
    board = BoardFactory(project=project)
    column = ColumnFactory(board=board)

    task = TaskFactory(
        project=project,
        board=board,
        column=column,
        created_by=owner,
        assignee=old_assignee,
    )

    update_task(
        task=task,
        actor=owner,
        title="Updated",
        description="Updated desc",
        priority=Task.Priority.HIGH,
        assignee=new_assignee,
        deadline=None,
    )

    task.refresh_from_db()

    assert task.assignee == new_assignee
    assert TaskActivity.objects.filter(
        task=task,
        action=TaskActivity.Action.ASSIGNEE_CHANGED,
    ).exists()


@pytest.mark.django_db
def test_archive_task_sets_is_archived_true():
    owner = UserFactory()
    workspace = WorkspaceFactory(owner=owner)

    WorkspaceMemberFactory(
        workspace=workspace,
        user=owner,
        role=WorkspaceMember.Role.OWNER,
    )

    project = ProjectFactory(workspace=workspace, created_by=owner)
    board = BoardFactory(project=project)
    column = ColumnFactory(board=board)

    task = TaskFactory(
        project=project,
        board=board,
        column=column,
        created_by=owner,
    )

    archive_task(task=task, actor=owner)

    task.refresh_from_db()
    assert task.is_archived is True