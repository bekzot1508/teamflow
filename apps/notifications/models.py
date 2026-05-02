from django.conf import settings
from django.db import models

from apps.common.models import TimeStampedModel
from apps.tasks.models import Task


class Notification(TimeStampedModel):
    class Type(models.TextChoices):
        TASK_ASSIGNED = "task_assigned", "Task Assigned"
        MENTIONED = "mentioned", "Mentioned in Comment"
        STATUS_CHANGED = "status_changed", "Status Changed"
        DEADLINE = "deadline", "Deadline Reminder"

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sent_notifications",
    )

    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    type = models.CharField(
        max_length=50,
        choices=Type.choices,
    )

    message = models.CharField(max_length=255)

    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.recipient} - {self.type}"