from django.db import transaction

from .models import Notification


def create_notification(*, recipient, actor=None, task=None, type, message):
    if recipient is None:
        return None

    if actor and recipient.id == actor.id:
        return None

    return Notification.objects.create(
        recipient=recipient,
        actor=actor,
        task=task,
        type=type,
        message=message,
    )


@transaction.atomic
def mark_notification_as_read(*, notification, user):
    if notification.recipient_id != user.id:
        return

    if notification.is_read:
        return

    notification.is_read = True
    notification.save(update_fields=["is_read"])


@transaction.atomic
def mark_all_notifications_as_read(*, user):
    Notification.objects.filter(
        recipient=user,
        is_read=False,
    ).update(is_read=True)