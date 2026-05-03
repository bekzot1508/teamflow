import pytest
import threading

from apps.tasks.services import change_task_status
from apps.tasks.models import Task
from tests.factories import (
    UserFactory,
    WorkspaceFactory,
    WorkspaceMemberFactory,
    ProjectFactory,
    BoardFactory,
    ColumnFactory,
    TaskFactory,
)
from apps.workspaces.models import WorkspaceMember
from apps.tasks.services import move_task_to_column


@pytest.mark.django_db(transaction=True)
def test_concurrent_status_update():
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
    column = ColumnFactory(board=board)

    task = TaskFactory(
        project=project,
        board=board,
        column=column,
        created_by=owner,
        assignee=member,
        status=Task.Status.IN_PROGRESS,
    )

    def worker():
        change_task_status(
            task=task,
            actor=member,
            new_status=Task.Status.REVIEW,
        )

    t1 = threading.Thread(target=worker)
    t2 = threading.Thread(target=worker)

    t1.start()
    t2.start()

    t1.join()
    t2.join()

    task.refresh_from_db()

    assert task.status == Task.Status.REVIEW


@pytest.mark.django_db
def test_idempotent_move_to_same_column():
    owner = UserFactory()
    workspace = WorkspaceFactory(owner=owner)

    WorkspaceMemberFactory(
        workspace=workspace,
        user=owner,
        role=WorkspaceMember.Role.OWNER,
    )

    project = ProjectFactory(workspace=workspace, created_by=owner)
    board = BoardFactory(project=project)
    todo_column = ColumnFactory(board=board, name="Todo", position=0)

    task = TaskFactory(
        project=project,
        board=board,
        column=todo_column,
        created_by=owner,
        status=Task.Status.TODO,
    )

    move_task_to_column(
        task=task,
        actor=owner,
        target_column=todo_column,
    )

    move_task_to_column(
        task=task,
        actor=owner,
        target_column=todo_column,
    )

    task.refresh_from_db()

    assert task.column == todo_column
    assert task.status == Task.Status.TODO

@pytest.mark.django_db
def test_transaction_rollback():
    user = UserFactory()
    task = TaskFactory(created_by=user)

    with pytest.raises(Exception):
        from django.db import transaction

        with transaction.atomic():
            task.title = "New Title"
            task.save()

            raise Exception("Force rollback")

    task.refresh_from_db()

    assert task.title != "New Title"