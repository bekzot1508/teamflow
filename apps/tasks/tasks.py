from celery import shared_task

from .services import check_deadline_reminders


@shared_task
def check_deadline_reminders_task():
    check_deadline_reminders()