import pytest

from apps.notifications.models import Notification
from apps.notifications.services import (
    create_notification,
    mark_all_notifications_as_read,
    mark_notification_as_read,
)
from apps.tasks.models import Task
from tests.factories import UserFactory, TaskFactory


@pytest.mark.django_db
def test_create_notification():
    recipient = UserFactory()
    actor = UserFactory()
    task = TaskFactory()

    notification = create_notification(
        recipient=recipient,
        actor=actor,
        task=task,
        type=Notification.Type.TASK_ASSIGNED,
        message="Assigned",
    )

    assert notification.recipient == recipient
    assert notification.actor == actor
    assert notification.task == task
    assert notification.is_read is False


@pytest.mark.django_db
def test_no_self_notification():
    user = UserFactory()
    task = TaskFactory()

    notification = create_notification(
        recipient=user,
        actor=user,
        task=task,
        type=Notification.Type.STATUS_CHANGED,
        message="Status changed",
    )

    assert notification is None
    assert Notification.objects.count() == 0


@pytest.mark.django_db
def test_mark_notification_as_read():
    user = UserFactory()
    notification = Notification.objects.create(
        recipient=user,
        type=Notification.Type.TASK_ASSIGNED,
        message="Test",
    )

    mark_notification_as_read(notification=notification, user=user)

    notification.refresh_from_db()
    assert notification.is_read is True


@pytest.mark.django_db
def test_mark_all_as_read():
    user = UserFactory()

    Notification.objects.create(
        recipient=user,
        type=Notification.Type.TASK_ASSIGNED,
        message="One",
    )
    Notification.objects.create(
        recipient=user,
        type=Notification.Type.STATUS_CHANGED,
        message="Two",
    )

    mark_all_notifications_as_read(user=user)

    assert Notification.objects.filter(recipient=user, is_read=False).count() == 0