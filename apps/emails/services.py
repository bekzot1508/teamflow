from django.conf import settings
from django.core.mail import send_mail


def send_task_assigned_email(*, task):
    if not task.assignee:
        return

    send_mail(
        subject=f"New task assigned: {task.title}",
        message=(
            f"You have been assigned a task.\n\n"
            f"Task: {task.title}\n"
            f"Project: {task.project.name}\n"
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[task.assignee.email],
        fail_silently=False,
    )


def send_mention_email(*, task, mentioned_user, actor):
    send_mail(
        subject=f"You were mentioned in task: {task.title}",
        message=(
            f"{actor.email} mentioned you in a comment.\n\n"
            f"Task: {task.title}\n"
            f"Project: {task.project.name}\n"
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[mentioned_user.email],
        fail_silently=False,
    )


def send_deadline_reminder_email(*, task):
    if not task.assignee:
        return

    send_mail(
        subject=f"Deadline approaching: {task.title}",
        message=(
            f"Task deadline is approaching.\n\n"
            f"Task: {task.title}\n"
            f"Deadline: {task.deadline}\n"
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[task.assignee.email],
        fail_silently=False,
    )