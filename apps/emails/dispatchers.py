import logging

from django.conf import settings
from django.db import transaction

from apps.emails.tasks import (
    send_task_assigned_email_task,
    send_mention_email_task,
    send_deadline_reminder_email_task,
)

logger = logging.getLogger(__name__)


def queue_task_assigned_email(task_id):
    if not settings.ENABLE_ASYNC_EMAILS:
        logger.info("Async email disabled. Skipping task assigned email. task_id=%s", task_id)
        return

    def _send():
        try:
            send_task_assigned_email_task.delay(task_id)
        except Exception:
            logger.exception("Failed to queue task assigned email. task_id=%s", task_id)

    transaction.on_commit(_send)


def queue_mention_email(task_id, mentioned_user_id, actor_id):
    if not settings.ENABLE_ASYNC_EMAILS:
        logger.info(
            "Async email disabled. Skipping mention email. task_id=%s user_id=%s",
            task_id,
            mentioned_user_id,
        )
        return

    def _send():
        try:
            send_mention_email_task.delay(task_id, mentioned_user_id, actor_id)
        except Exception:
            logger.exception("Failed to queue mention email. task_id=%s", task_id)

    transaction.on_commit(_send)


def queue_deadline_reminder_email(task_id):
    if not settings.ENABLE_ASYNC_EMAILS:
        logger.info("Async email disabled. Skipping deadline email. task_id=%s", task_id)
        return

    def _send():
        try:
            send_deadline_reminder_email_task.delay(task_id)
        except Exception:
            logger.exception("Failed to queue deadline email. task_id=%s", task_id)

    transaction.on_commit(_send)