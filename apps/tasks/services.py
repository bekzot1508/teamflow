from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction

from apps.workspaces.models import WorkspaceMember
from apps.workspaces.permissions import can_create_task, can_update_task

from .models import Task, TaskActivity
from .selectors import get_next_task_position


ALLOWED_TRANSITIONS = {
    Task.Status.TODO: [Task.Status.IN_PROGRESS],
    Task.Status.IN_PROGRESS: [Task.Status.REVIEW],
    Task.Status.REVIEW: [Task.Status.DONE, Task.Status.IN_PROGRESS],
    Task.Status.DONE: [],
}


def _ensure_assignee_is_workspace_member(*, project, assignee):
    if assignee is None:
        return

    exists = WorkspaceMember.objects.filter(
        workspace=project.workspace,
        user=assignee,
    ).exists()

    if not exists:
        raise ValidationError("Assignee must be a workspace member.")


def create_task_activity(*, task, actor, action, old_value="", new_value=""):
    return TaskActivity.objects.create(
        task=task,
        actor=actor,
        action=action,
        old_value=old_value,
        new_value=new_value,
    )


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

    return task


@transaction.atomic
def change_task_status(*, task, actor, new_status):
    task = Task.objects.select_for_update().get(id=task.id)

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

    return task