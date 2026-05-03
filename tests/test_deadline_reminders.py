import pytest
from django.utils import timezone
from datetime import timedelta

from apps.notifications.models import Notification
from apps.tasks.models import Task
from apps.tasks.services import check_deadline_reminders
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
def deadline_setup():
    owner = UserFactory()
    assignee = UserFactory()

    workspace = WorkspaceFactory(owner=owner)

    WorkspaceMemberFactory(workspace=workspace, user=owner, role=WorkspaceMember.Role.OWNER)
    WorkspaceMemberFactory(workspace=workspace, user=assignee, role=WorkspaceMember.Role.MEMBER)

    project = ProjectFactory(workspace=workspace, created_by=owner)
    board = BoardFactory(project=project)
    column = ColumnFactory(board=board, name="Todo", position=0)

    return owner, assignee, project, board, column


@pytest.mark.django_db
def test_deadline_reminder_creates_notification(deadline_setup):
    owner, assignee, project, board, column = deadline_setup

    task = TaskFactory(
        project=project,
        board=board,
        column=column,
        created_by=owner,
        assignee=assignee,
        deadline=timezone.now() + timedelta(hours=2),
        deadline_reminder_sent=False,
        status=Task.Status.IN_PROGRESS,
    )

    check_deadline_reminders()

    task.refresh_from_db()

    assert task.deadline_reminder_sent is True
    assert Notification.objects.filter(
        recipient=assignee,
        task=task,
        type=Notification.Type.DEADLINE,
    ).exists()


@pytest.mark.django_db
def test_deadline_reminder_not_sent_for_done_task(deadline_setup):
    owner, assignee, project, board, column = deadline_setup

    task = TaskFactory(
        project=project,
        board=board,
        column=column,
        created_by=owner,
        assignee=assignee,
        deadline=timezone.now() + timedelta(hours=2),
        deadline_reminder_sent=False,
        status=Task.Status.DONE,
    )

    check_deadline_reminders()

    task.refresh_from_db()

    assert task.deadline_reminder_sent is False
    assert not Notification.objects.filter(task=task).exists()


@pytest.mark.django_db
def test_deadline_reminder_not_sent_twice(deadline_setup):
    owner, assignee, project, board, column = deadline_setup

    task = TaskFactory(
        project=project,
        board=board,
        column=column,
        created_by=owner,
        assignee=assignee,
        deadline=timezone.now() + timedelta(hours=2),
        deadline_reminder_sent=False,
        status=Task.Status.IN_PROGRESS,
    )

    check_deadline_reminders()
    check_deadline_reminders()

    assert Notification.objects.filter(
        recipient=assignee,
        task=task,
        type=Notification.Type.DEADLINE,
    ).count() == 1