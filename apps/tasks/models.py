from django.conf import settings
from django.db import models

from apps.common.models import TimeStampedModel
from apps.projects.models import Project, Board, Column


class Task(TimeStampedModel):
    class Priority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        URGENT = "urgent", "Urgent"

    class Status(models.TextChoices):
        TODO = "todo", "Todo"
        IN_PROGRESS = "in_progress", "In Progress"
        REVIEW = "review", "Review"
        DONE = "done", "Done"

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="tasks",
    )
    board = models.ForeignKey(
        Board,
        on_delete=models.CASCADE,
        related_name="tasks",
    )
    column = models.ForeignKey(
        Column,
        on_delete=models.CASCADE,
        related_name="tasks",
    )

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    priority = models.CharField(
        max_length=20,
        choices=Priority.choices,
        default=Priority.MEDIUM,
    )
    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.TODO,
    )

    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="assigned_tasks",
        blank=True,
        null=True,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_tasks",
    )

    deadline = models.DateTimeField(blank=True, null=True)
    position = models.PositiveIntegerField(default=0)
    is_archived = models.BooleanField(default=False)

    class Meta:
        ordering = ("position", "-created_at")

    def __str__(self):
        return self.title


class TaskActivity(TimeStampedModel):
    class Action(models.TextChoices):
        TASK_CREATED = "task_created", "Task Created"
        TASK_UPDATED = "task_updated", "Task Updated"
        STATUS_CHANGED = "status_changed", "Status Changed"
        ASSIGNEE_CHANGED = "assignee_changed", "Assignee Changed"
        DEADLINE_CHANGED = "deadline_changed", "Deadline Changed"
        COMMENT_ADDED = "comment_added", "Comment Added"
        FILE_ATTACHED = "file_attached", "File Attached"

    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name="activities",
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="task_activities",
        blank=True,
        null=True,
    )
    action = models.CharField(
        max_length=50,
        choices=Action.choices,
    )
    old_value = models.TextField(blank=True)
    new_value = models.TextField(blank=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.task} - {self.action}"