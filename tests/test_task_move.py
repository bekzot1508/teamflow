import pytest
from django.core.exceptions import PermissionDenied, ValidationError

from apps.tasks.models import Task, TaskActivity
from apps.tasks.services import move_task_to_column
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
def kanban():
    owner = UserFactory()
    member = UserFactory()
    viewer = UserFactory()

    workspace = WorkspaceFactory(owner=owner)

    WorkspaceMemberFactory(workspace=workspace, user=owner, role=WorkspaceMember.Role.OWNER)
    WorkspaceMemberFactory(workspace=workspace, user=member, role=WorkspaceMember.Role.MEMBER)
    WorkspaceMemberFactory(workspace=workspace, user=viewer, role=WorkspaceMember.Role.VIEWER)

    project = ProjectFactory(workspace=workspace, created_by=owner)
    board = BoardFactory(project=project)

    todo = ColumnFactory(board=board, name="Todo", position=0)
    doing = ColumnFactory(board=board, name="In Progress", position=1)
    review = ColumnFactory(board=board, name="Review", position=2)
    done = ColumnFactory(board=board, name="Done", position=3)

    task = TaskFactory(
        project=project,
        board=board,
        column=todo,
        status=Task.Status.TODO,
        created_by=owner,
        assignee=member,
        position=0,
    )

    return owner, member, viewer, project, board, task, todo, doing, review, done


@pytest.mark.django_db
def test_viewer_cannot_move_task(kanban):
    owner, member, viewer, project, board, task, todo, doing, review, done = kanban

    with pytest.raises(PermissionDenied):
        move_task_to_column(
            task=task,
            actor=viewer,
            target_column=doing,
        )


@pytest.mark.django_db
def test_task_cannot_move_to_column_from_another_board(kanban):
    owner, member, viewer, project, board, task, todo, doing, review, done = kanban

    another_board = BoardFactory(project=project)
    foreign_column = ColumnFactory(board=another_board, name="In Progress", position=0)

    with pytest.raises(ValidationError):
        move_task_to_column(
            task=task,
            actor=member,
            target_column=foreign_column,
        )


@pytest.mark.django_db
def test_move_creates_activity_log(kanban):
    owner, member, viewer, project, board, task, todo, doing, review, done = kanban

    move_task_to_column(
        task=task,
        actor=member,
        target_column=doing,
    )

    assert TaskActivity.objects.filter(
        task=task,
        action=TaskActivity.Action.STATUS_CHANGED,
    ).exists()


@pytest.mark.django_db
def test_move_todo_to_review_invalid(kanban):
    owner, member, viewer, project, board, task, todo, doing, review, done = kanban

    with pytest.raises(ValidationError):
        move_task_to_column(
            task=task,
            actor=member,
            target_column=review,
        )


@pytest.mark.django_db
def test_move_full_flow_to_done(kanban):
    owner, member, viewer, project, board, task, todo, doing, review, done = kanban

    move_task_to_column(task=task, actor=member, target_column=doing)
    task.refresh_from_db()

    move_task_to_column(task=task, actor=member, target_column=review)
    task.refresh_from_db()

    move_task_to_column(task=task, actor=member, target_column=done)
    task.refresh_from_db()

    assert task.status == Task.Status.DONE
    assert task.column == done