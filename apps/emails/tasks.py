import logging

from celery import shared_task
from django.contrib.auth import get_user_model

from apps.tasks.models import Task
from apps.emails.services import (
    send_task_assigned_email,
    send_mention_email,
    send_deadline_reminder_email,
)

logger = logging.getLogger(__name__)
User = get_user_model()


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_task_assigned_email_task(self, task_id):
    try:
        task = (
            Task.objects
            .select_related("project", "assignee")
            .get(id=task_id)
        )
        send_task_assigned_email(task=task)
        logger.info("Task assigned email sent. task_id=%s", task_id)

    except Exception as exc:
        logger.exception("Task assigned email failed. task_id=%s", task_id)
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_mention_email_task(self, task_id, mentioned_user_id, actor_id):
    try:
        task = Task.objects.select_related("project").get(id=task_id)
        mentioned_user = User.objects.get(id=mentioned_user_id)
        actor = User.objects.get(id=actor_id)

        send_mention_email(
            task=task,
            mentioned_user=mentioned_user,
            actor=actor,
        )
        logger.info(
            "Mention email sent. task_id=%s mentioned_user_id=%s",
            task_id,
            mentioned_user_id,
        )

    except Exception as exc:
        logger.exception(
            "Mention email failed. task_id=%s mentioned_user_id=%s",
            task_id,
            mentioned_user_id,
        )
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_deadline_reminder_email_task(self, task_id):
    try:
        task = (
            Task.objects
            .select_related("project", "assignee")
            .get(id=task_id)
        )

        send_deadline_reminder_email(task=task)
        logger.info("Deadline reminder email sent. task_id=%s", task_id)

    except Exception as exc:
        logger.exception("Deadline reminder email failed. task_id=%s", task_id)
        raise self.retry(exc=exc)