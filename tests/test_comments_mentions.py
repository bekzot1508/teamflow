import pytest

from apps.notifications.models import Notification
from apps.tasks.models import TaskActivity
from apps.tasks.services import create_task_comment
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
def comment_setup():
    owner = UserFactory(username="owner", email="owner@example.com")
    mentioned = UserFactory(username="ali", email="ali@example.com")
    outsider = UserFactory(username="outsider", email="outsider@example.com")

    workspace = WorkspaceFactory(owner=owner)

    WorkspaceMemberFactory(workspace=workspace, user=owner, role=WorkspaceMember.Role.OWNER)
    WorkspaceMemberFactory(workspace=workspace, user=mentioned, role=WorkspaceMember.Role.MEMBER)

    project = ProjectFactory(workspace=workspace, created_by=owner)
    board = BoardFactory(project=project)
    column = ColumnFactory(board=board, name="Todo", position=0)

    task = TaskFactory(
        project=project,
        board=board,
        column=column,
        created_by=owner,
    )

    return owner, mentioned, outsider, task


@pytest.mark.django_db
def test_create_comment_success(comment_setup):
    owner, mentioned, outsider, task = comment_setup

    comment = create_task_comment(
        task=task,
        author=owner,
        body="Hello team",
    )

    assert comment.task == task
    assert comment.author == owner
    assert comment.body == "Hello team"


@pytest.mark.django_db
def test_comment_creates_activity(comment_setup):
    owner, mentioned, outsider, task = comment_setup

    create_task_comment(
        task=task,
        author=owner,
        body="Activity test",
    )

    assert TaskActivity.objects.filter(
        task=task,
        action=TaskActivity.Action.COMMENT_ADDED,
    ).exists()


@pytest.mark.django_db
def test_mention_creates_notification(comment_setup):
    owner, mentioned, outsider, task = comment_setup

    create_task_comment(
        task=task,
        author=owner,
        body="@ali please check this",
    )

    assert Notification.objects.filter(
        recipient=mentioned,
        task=task,
        type=Notification.Type.MENTIONED,
    ).exists()


@pytest.mark.django_db
def test_duplicate_mentions_create_single_notification(comment_setup):
    owner, mentioned, outsider, task = comment_setup

    create_task_comment(
        task=task,
        author=owner,
        body="@ali @ali @ali check this",
    )

    assert Notification.objects.filter(
        recipient=mentioned,
        task=task,
        type=Notification.Type.MENTIONED,
    ).count() == 1


@pytest.mark.django_db
def test_outsider_mention_does_not_create_notification(comment_setup):
    owner, mentioned, outsider, task = comment_setup

    create_task_comment(
        task=task,
        author=owner,
        body="@outsider hello",
    )

    assert not Notification.objects.filter(
        recipient=outsider,
        task=task,
        type=Notification.Type.MENTIONED,
    ).exists()