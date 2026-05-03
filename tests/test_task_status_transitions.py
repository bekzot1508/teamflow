import pytest
from django.core.exceptions import PermissionDenied, ValidationError

from apps.tasks.models import Task
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
def kanban_setup():
    owner = UserFactory()
    member = UserFactory()

    workspace = WorkspaceFactory(owner=owner)

    WorkspaceMemberFactory(
        workspace=workspace,
        user=owner,
        role=WorkspaceMember.Role.OWNER,
    )
    WorkspaceMemberFactory(
        workspace=workspace,
        user=member,
        role=WorkspaceMember.Role.MEMBER,
    )

    project = ProjectFactory(workspace=workspace, created_by=owner)
    board = BoardFactory(project=project)

    todo = ColumnFactory(board=board, name="Todo", position=0)
    in_progress = ColumnFactory(board=board, name="In Progress", position=1)
    review = ColumnFactory(board=board, name="Review", position=2)
    done = ColumnFactory(board=board, name="Done", position=3)

    task = TaskFactory(
        project=project,
        board=board,
        column=todo,
        created_by=owner,
        assignee=member,
        status=Task.Status.TODO,
    )

    return owner, member, task, todo, in_progress, review, done


@pytest.mark.django_db
def test_move_todo_to_in_progress_allowed(kanban_setup):
    owner, member, task, todo, in_progress, review, done = kanban_setup

    move_task_to_column(
        task=task,
        actor=member,
        target_column=in_progress,
    )

    task.refresh_from_db()

    assert task.column == in_progress
    assert task.status == Task.Status.IN_PROGRESS


@pytest.mark.django_db
def test_move_todo_to_done_not_allowed(kanban_setup):
    owner, member, task, todo, in_progress, review, done = kanban_setup

    with pytest.raises(ValidationError):
        move_task_to_column(
            task=task,
            actor=member,
            target_column=done,
        )


@pytest.mark.django_db
def test_move_review_to_done_allowed(kanban_setup):
    owner, member, task, todo, in_progress, review, done = kanban_setup

    task.status = Task.Status.REVIEW
    task.column = review
    task.save(update_fields=["status", "column"])

    move_task_to_column(
        task=task,
        actor=member,
        target_column=done,
    )

    task.refresh_from_db()

    assert task.column == done
    assert task.status == Task.Status.DONE


@pytest.mark.django_db
def test_member_cannot_reopen_done_task(kanban_setup):
    owner, member, task, todo, in_progress, review, done = kanban_setup

    task.status = Task.Status.DONE
    task.column = done
    task.save(update_fields=["status", "column"])

    with pytest.raises(PermissionDenied):
        move_task_to_column(
            task=task,
            actor=member,
            target_column=in_progress,
        )


@pytest.mark.django_db
def test_owner_can_reopen_done_task(kanban_setup):
    owner, member, task, todo, in_progress, review, done = kanban_setup

    task.status = Task.Status.DONE
    task.column = done
    task.save(update_fields=["status", "column"])

    move_task_to_column(
        task=task,
        actor=owner,
        target_column=in_progress,
    )

    task.refresh_from_db()

    assert task.column == in_progress
    assert task.status == Task.Status.IN_PROGRESS


@pytest.mark.django_db
def test_move_to_same_column_is_idempotent(kanban_setup):
    owner, member, task, todo, in_progress, review, done = kanban_setup

    move_task_to_column(
        task=task,
        actor=member,
        target_column=todo,
    )

    move_task_to_column(
        task=task,
        actor=member,
        target_column=todo,
    )

    task.refresh_from_db()

    assert task.column == todo
    assert task.status == Task.Status.TODO


@pytest.mark.django_db
def test_move_task_to_target_position(kanban_setup):
    owner, member, task, todo, in_progress, review, done = kanban_setup

    task_2 = TaskFactory(
        project=task.project,
        board=task.board,
        column=in_progress,
        created_by=owner,
        status=Task.Status.IN_PROGRESS,
        position=0,
    )

    task_3 = TaskFactory(
        project=task.project,
        board=task.board,
        column=in_progress,
        created_by=owner,
        status=Task.Status.IN_PROGRESS,
        position=1,
    )

    move_task_to_column(
        task=task,
        actor=member,
        target_column=in_progress,
        target_position=0,
    )

    task.refresh_from_db()
    task_2.refresh_from_db()
    task_3.refresh_from_db()

    assert task.column == in_progress
    assert task.position == 0
    assert task_2.position == 1
    assert task_3.position == 2