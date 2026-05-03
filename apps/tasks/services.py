from django.core.exceptions import PermissionDenied, ValidationError
from django.db import models
from django.db import transaction
from django.utils.text import get_valid_filename
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import re
import os
import mimetypes

from .models import Task, TaskActivity, TaskAttachment, TaskComment
from apps.workspaces.models import WorkspaceMember
from apps.notifications.models import Notification
from apps.notifications.services import create_notification
from apps.workspaces.permissions import can_create_task, can_update_task

from .selectors import get_next_task_position, normalize_column_positions
# from apps.emails.tasks import (
#     send_task_assigned_email_task,
#     send_mention_email_task,
#     send_deadline_reminder_email_task
# )
from apps.emails.dispatchers import (
    queue_task_assigned_email,
    queue_mention_email,
    queue_deadline_reminder_email,
)



User = get_user_model()


ALLOWED_TRANSITIONS = {
    Task.Status.TODO: [Task.Status.IN_PROGRESS],
    Task.Status.IN_PROGRESS: [Task.Status.REVIEW],
    Task.Status.REVIEW: [Task.Status.DONE, Task.Status.IN_PROGRESS],
    Task.Status.DONE: [],
}

COLUMN_STATUS_MAP = {
    "Todo": Task.Status.TODO,
    "In Progress": Task.Status.IN_PROGRESS,
    "Review": Task.Status.REVIEW,
    "Done": Task.Status.DONE,
}

MENTION_PATTERN = r"@([\w.@+-]+)"

ALLOWED_ATTACHMENT_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".pdf", ".txt", ".docx"
}

ALLOWED_ATTACHMENT_MIME_TYPES = {
    "image/png",
    "image/jpeg",
    "application/pdf",
    "text/plain",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}

MAX_ATTACHMENT_SIZE = 5 * 1024 * 1024 # 5MB


def _ensure_assignee_is_workspace_member(*, project, assignee):
    if assignee is None:
        return

    exists = WorkspaceMember.objects.filter(
        workspace=project.workspace,
        user=assignee,
    ).exists()

    if not exists:
        raise ValidationError("Assignee must be a workspace member.")


#____________ Create Task Activity ____________#
def create_task_activity(*, task, actor, action, old_value="", new_value=""):
    return TaskActivity.objects.create(
        task=task,
        actor=actor,
        action=action,
        old_value=old_value,
        new_value=new_value,
    )


#____________ Create Task ____________#
@transaction.atomic
def create_task(
    *,
    project,
    board,
    column,
    actor,
    title,
    description="",
    priority=Task.Priority.MEDIUM,
    assignee=None,
    deadline=None,
):
    if not can_create_task(actor, project.workspace):
        raise PermissionDenied("You cannot create task in this workspace.")

    if board.project_id != project.id:
        raise ValidationError("Board does not belong to this project.")

    if column.board_id != board.id:
        raise ValidationError("Column does not belong to this board.")

    _ensure_assignee_is_workspace_member(project=project, assignee=assignee)

    position = get_next_task_position(column=column)

    task = Task.objects.create(
        project=project,
        board=board,
        column=column,
        title=title,
        description=description,
        priority=priority,
        assignee=assignee,
        created_by=actor,
        deadline=deadline,
        position=position,
    )

    create_task_activity(
        task=task,
        actor=actor,
        action=TaskActivity.Action.TASK_CREATED,
        new_value=task.title,
    )

    if task.assignee:
        create_notification(
            recipient=task.assignee,
            actor=actor,
            task=task,
            type=Notification.Type.TASK_ASSIGNED,
            message=f"You were assigned to task: {task.title}",
        )

        # serverda background worker chargable bo'lgani uchun productionda celery ishlatmay turamiz
        # transaction.on_commit(
        #     lambda: send_task_assigned_email_task.delay(task.id)
        # )
        transaction.on_commit(
            lambda: queue_task_assigned_email(task.id)
        )

    return task


#____________ Change Task Status ____________#
@transaction.atomic
def change_task_status(*, task, actor, new_status):
    task = Task.objects.select_for_update().get(id=task.id)

    # 🔥 IDENTITY CHECK (ENG MUHIM)
    if task.status == new_status:
        return task

    if not can_update_task(actor, task.project.workspace):
        raise PermissionDenied("You cannot update this task.")

    if task.status == Task.Status.DONE:
        actor_role = WorkspaceMember.objects.filter(
            workspace=task.project.workspace,
            user=actor,
        ).values_list("role", flat=True).first()

        if actor_role not in [
            WorkspaceMember.Role.OWNER,
            WorkspaceMember.Role.ADMIN,
        ]:
            raise PermissionDenied("Only owner/admin can reopen done task.")

    allowed = ALLOWED_TRANSITIONS.get(task.status, [])

    if new_status not in allowed and not (
        task.status == Task.Status.DONE and new_status != Task.Status.DONE
    ):
        raise ValidationError("Invalid task status transition.")

    old_status = task.status
    task.status = new_status
    task.save(update_fields=["status", "updated_at"])

    create_task_activity(
        task=task,
        actor=actor,
        action=TaskActivity.Action.STATUS_CHANGED,
        old_value=old_status,
        new_value=new_status,
    )

    if task.assignee:
        create_notification(
            recipient=task.assignee,
            actor=actor,
            task=task,
            type=Notification.Type.STATUS_CHANGED,
            message=f"Task status changed: {task.title} → {task.get_status_display()}",
        )
    return task


#____________ Move Task columns ____________#
@transaction.atomic
def move_task_to_column(*, task, actor, target_column, target_position=None):
    task = (
        Task.objects
        .select_for_update()
        .select_related("project", "project__workspace", "column", "board")
        .get(id=task.id)
    )

    if not can_update_task(actor, task.project.workspace):
        raise PermissionDenied("You cannot move this task.")

    if task.column_id == target_column.id:
        return task

    if target_column.board_id != task.board_id:
        raise ValidationError("Target column does not belong to this board.")

    old_column = task.column
    old_column_name = task.column.name
    old_status = task.status

    new_status = COLUMN_STATUS_MAP.get(target_column.name)

    if new_status is None:
        raise ValidationError("Unknown column status mapping.")

    if new_status != task.status:
        if task.status == Task.Status.DONE:
            actor_role = WorkspaceMember.objects.filter(
                workspace=task.project.workspace,
                user=actor,
            ).values_list("role", flat=True).first()

            if actor_role not in [
                WorkspaceMember.Role.OWNER,
                WorkspaceMember.Role.ADMIN,
            ]:
                raise PermissionDenied("Only owner/admin can reopen done task.")

        elif new_status not in ALLOWED_TRANSITIONS.get(task.status, []):
            raise ValidationError("Invalid task move/status transition.")

    if target_position is None:
        target_position = get_next_task_position(column=target_column)

    target_position = max(int(target_position), 0)

    # Shift tasks in target column
    Task.objects.filter(
        column=target_column,
        is_archived=False,
        position__gte=target_position,
    ).exclude(id=task.id).update(
        position=models.F("position") + 1
    )

    task.column = target_column
    task.status = new_status
    task.position = target_position
    task.save(update_fields=["column", "status", "position", "updated_at"])

    normalize_column_positions(column=old_column)
    normalize_column_positions(column=target_column)

    create_task_activity(
        task=task,
        actor=actor,
        action=TaskActivity.Action.STATUS_CHANGED,
        old_value=f"{old_column_name} / {old_status}",
        new_value=f"{target_column.name} / {new_status}",
    )

    if task.assignee:
        create_notification(
            recipient=task.assignee,
            actor=actor,
            task=task,
            type=Notification.Type.STATUS_CHANGED,
            message=f"Task moved to {target_column.name}: {task.title}",
        )

    return task

#____________ Update Task ____________#
@transaction.atomic
def update_task(
    *,
    task,
    actor,
    title,
    description,
    priority,
    assignee,
    deadline,
):
    task = (
        Task.objects
        .select_for_update()
        .select_related("project", "project__workspace")
        .get(id=task.id)
    )

    if not can_update_task(actor, task.project.workspace):
        raise PermissionDenied("You cannot update this task.")

    _ensure_assignee_is_workspace_member(
        project=task.project,
        assignee=assignee,
    )

    old_assignee = task.assignee.email if task.assignee else ""
    new_assignee = assignee.email if assignee else ""

    old_deadline = str(task.deadline) if task.deadline else ""
    new_deadline = str(deadline) if deadline else ""

    task.title = title
    task.description = description
    task.priority = priority
    task.assignee = assignee
    task.deadline = deadline

    task.save(update_fields=[
        "title",
        "description",
        "priority",
        "assignee",
        "deadline",
        "updated_at",
    ])

    create_task_activity(
        task=task,
        actor=actor,
        action=TaskActivity.Action.TASK_UPDATED,
        old_value="Task updated",
        new_value=task.title,
    )

    if old_assignee != new_assignee:
        create_task_activity(
            task=task,
            actor=actor,
            action=TaskActivity.Action.ASSIGNEE_CHANGED,
            old_value=old_assignee,
            new_value=new_assignee,
        )

    if old_assignee != new_assignee and assignee:

        create_notification(
            recipient=assignee,
            actor=actor,
            task=task,
            type=Notification.Type.TASK_ASSIGNED,
            message=f"You were assigned to task: {task.title}",
        )

        # serverda background worker chargable bo'lgani uchun productionda celery ishlatmay turamiz
        # transaction.on_commit(
        #     lambda: send_task_assigned_email_task.delay(task.id)
        # )
        transaction.on_commit(
            lambda: queue_task_assigned_email(task.id)
        )

    if old_deadline != new_deadline:
        create_task_activity(
            task=task,
            actor=actor,
            action=TaskActivity.Action.DEADLINE_CHANGED,
            old_value=old_deadline,
            new_value=new_deadline,
        )

    return task


#____________ Archive Task ____________#
@transaction.atomic
def archive_task(*, task, actor):
    task = (
        Task.objects
        .select_for_update()
        .select_related("project", "project__workspace")
        .get(id=task.id)
    )

    if not can_update_task(actor, task.project.workspace):
        raise PermissionDenied("You cannot archive this task.")

    if task.is_archived:
        return task

    task.is_archived = True
    task.save(update_fields=["is_archived", "updated_at"])

    create_task_activity(
        task=task,
        actor=actor,
        action=TaskActivity.Action.TASK_UPDATED,
        old_value="is_archived=False",
        new_value="is_archived=True",
    )

    return task


#____________ Helper Function ____________#
def extract_mentions(text):
    return re.findall(MENTION_PATTERN, text)


#____________ Task Comment create service ____________#
@transaction.atomic
def create_task_comment(*, task, author, body):
    comment = TaskComment.objects.create(
        task=task,
        author=author,
        body=body,
    )

    create_task_activity(
        task=task,
        actor=author,
        action=TaskActivity.Action.COMMENT_ADDED,
        new_value=body[:100],
    )

    usernames = set(extract_mentions(body))

    usernames = set(extract_mentions(body))

    if usernames:
        mentioned_users = User.objects.filter(
            username__in=usernames,
            workspace_memberships__workspace=task.project.workspace,
        ).distinct()

        for user in mentioned_users:
            create_notification(
                recipient=user,
                actor=author,
                task=task,
                type=Notification.Type.MENTIONED,
                message=f"{author.email} mentioned you in a comment: {task.title}",
            )

            # serverda background worker chargable bo'lgani uchun productionda celery ishlatmay turamiz
            # transaction.on_commit(
            #     lambda user_id=user.id: send_mention_email_task.delay(
            #         task.id,
            #         user_id,
            #         author.id,
            #     )
            # )
            transaction.on_commit(
                lambda user_id=user.id: queue_mention_email(task.id, user.id, author.id)
            )

    return comment



#____________ Check Deadline reminders ____________#
def check_deadline_reminders():
    now = timezone.now()
    soon = now + timedelta(hours=24)

    tasks = (
        Task.objects
        .filter(
            deadline__isnull=False,
            deadline__lte=soon,
            deadline__gte=now,
            status__in=[
                Task.Status.TODO,
                Task.Status.IN_PROGRESS,
                Task.Status.REVIEW,
            ],
            deadline_reminder_sent=False,
        )
        .select_related("assignee")
    )

    for task in tasks:
        if not task.assignee:
            continue

        # Notification
        Notification.objects.create(
            recipient=task.assignee,
            actor=None,
            task=task,
            type=Notification.Type.DEADLINE,
            message=f"Deadline is upcoming: {task.title}",
        )

        # Email (async)
        # serverda background worker chargable bo'lgani uchun productionda celery ishlatmay turamiz
        # send_deadline_reminder_email_task.delay(task.id)
        queue_deadline_reminder_email(task.id)

        # Mark as sent
        task.deadline_reminder_sent = True
        task.save(update_fields=["deadline_reminder_sent"])


#____________ Attachment service ____________#
@transaction.atomic
def attach_file_to_task(*, task, actor, uploaded_file):
    task = (
        Task.objects
        .select_for_update()
        .select_related("project", "project__workspace")
        .get(id=task.id)
    )

    if not can_update_task(actor, task.project.workspace):
        raise PermissionDenied("You cannot attach files to this task.")

    original_name = uploaded_file.name
    safe_name = get_valid_filename(original_name)

    ext = os.path.splitext(safe_name)[1].lower()

    if ext not in ALLOWED_ATTACHMENT_EXTENSIONS:
        raise ValidationError("File type is not allowed.")

    if uploaded_file.size > MAX_ATTACHMENT_SIZE:
        raise ValidationError("File size must be less than 5MB.")

    guessed_mime, _ = mimetypes.guess_type(safe_name)

    if guessed_mime not in ALLOWED_ATTACHMENT_MIME_TYPES:
        raise ValidationError("Invalid file MIME type.")

    attachment = TaskAttachment.objects.create(
        task=task,
        uploaded_by=actor,
        file=uploaded_file,
        original_filename=safe_name,
        file_size=uploaded_file.size,
    )

    create_task_activity(
        task=task,
        actor=actor,
        action=TaskActivity.Action.FILE_ATTACHED,
        new_value=safe_name,
    )

    return attachment


@transaction.atomic
def delete_task_attachment(*, attachment, actor):
    task = (
        Task.objects
        .select_for_update()
        .select_related("project", "project__workspace")
        .get(id=attachment.task_id)
    )

    if not can_update_task(actor, task.project.workspace):
        raise PermissionDenied("You cannot delete this attachment.")

    filename = attachment.original_filename

    attachment.file.delete(save=False)
    attachment.delete()

    create_task_activity(
        task=task,
        actor=actor,
        action=TaskActivity.Action.TASK_UPDATED,
        old_value=f"Attachment: {filename}",
        new_value="Attachment deleted",
    )