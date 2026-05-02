from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import PermissionDenied, ValidationError
from django.views import View

from .models import Task, TaskAttachment
from apps.projects.models import Project, Column

from apps.workspaces.permissions import can_create_task
from .forms import TaskCreateForm, TaskUpdateForm, TaskCommentForm, TaskAttachmentForm
from .services import (
    create_task,
    move_task_to_column,
    update_task,
    archive_task,
    create_task_comment,
    attach_file_to_task,
    delete_task_attachment
    )
from .selectors import get_task_detail

User = get_user_model()


#____________ Task Create ____________#
class TaskCreateView(LoginRequiredMixin, View):
    template_name = "tasks/task_form.html"

    def get(self, request, project_id):
        project = get_object_or_404(Project, id=project_id)

        if not can_create_task(request.user, project.workspace):
            messages.error(request, "Permission denied")
            return redirect("projects:detail", project_id=project.id)

        form = TaskCreateForm()

        # ⚠️ assignee faqat workspace memberlar bo‘lishi kerak
        form.fields["assignee"].queryset = User.objects.filter(
            workspace_memberships__workspace=project.workspace
        )

        return render(request, self.template_name, {
            "form": form,
            "project": project,
        })


    def post(self, request, project_id):
        project = get_object_or_404(Project, id=project_id)

        if not can_create_task(request.user, project.workspace):
            messages.error(request, "Permission denied")
            return redirect("projects:detail", project_id=project.id)

        form = TaskCreateForm(request.POST)

        form.fields["assignee"].queryset = User.objects.filter(
            workspace_memberships__workspace=project.workspace
        )

        if form.is_valid():
            board = project.boards.first()
            column = board.columns.first()

            create_task(
                project=project,
                board=board,
                column=column,
                actor=request.user,
                title=form.cleaned_data["title"],
                description=form.cleaned_data["description"],
                priority=form.cleaned_data["priority"],
                assignee=form.cleaned_data["assignee"],
                deadline=form.cleaned_data["deadline"],
            )

            messages.success(request, "Task created successfully")
            return redirect("projects:detail", project_id=project.id)

        return render(request, self.template_name, {
            "form": form,
            "project": project,
        })




#____________ Task Detail ____________#
class TaskDetailView(LoginRequiredMixin, View):
    template_name = "tasks/task_detail.html"

    def get(self, request, task_id):
        task = get_task_detail(
            task_id=task_id,
            user=request.user,
        )

        if task is None:
            messages.error(request, "Task not found")
            return redirect("workspaces:list")

        return render(request, self.template_name, {
            "task": task,
        })


#____________ Task column Move ____________#
class TaskMoveView(LoginRequiredMixin, View):
    def post(self, request, task_id):
        task = get_object_or_404(Task, id=task_id)
        target_column = get_object_or_404(
            Column,
            id=request.POST.get("column_id"),
        )

        try:
            move_task_to_column(
                task=task,
                actor=request.user,
                target_column=target_column,
            )
            messages.success(request, "Task moved successfully.")

        except (ValidationError, PermissionDenied) as exc:
            messages.error(request, str(exc))

        return redirect("projects:detail", project_id=task.project_id)


#____________ Task Update ____________#
class TaskUpdateView(LoginRequiredMixin, View):
    template_name = "tasks/task_form.html"

    def get(self, request, task_id):
        task = get_task_detail(task_id=task_id, user=request.user)

        if task is None:
            messages.error(request, "Task not found or access denied.")
            return redirect("workspaces:list")

        form = TaskUpdateForm(instance=task)

        User = task.assignee.__class__ if task.assignee else None

        form.fields["assignee"].queryset = User.objects.filter(
            workspace_memberships__workspace=task.project.workspace
        )

        return render(request, self.template_name, {
            "form": form,
            "project": task.project,
            "task": task,
            "is_update": True,
        })

    def post(self, request, task_id):
        task = get_task_detail(task_id=task_id, user=request.user)

        if task is None:
            messages.error(request, "Task not found or access denied.")
            return redirect("workspaces:list")

        form = TaskUpdateForm(request.POST, instance=task)

        form.fields["assignee"].queryset = User.objects.filter(
            workspace_memberships__workspace=task.project.workspace
        )

        if form.is_valid():
            try:
                task = update_task(
                    task=task,
                    actor=request.user,
                    title=form.cleaned_data["title"],
                    description=form.cleaned_data["description"],
                    priority=form.cleaned_data["priority"],
                    assignee=form.cleaned_data["assignee"],
                    deadline=form.cleaned_data["deadline"],
                )
                messages.success(request, "Task updated successfully.")
                return redirect("tasks:detail", task_id=task.id)

            except (ValidationError, PermissionDenied) as exc:
                messages.error(request, str(exc))

        return render(request, self.template_name, {
            "form": form,
            "project": task.project,
            "task": task,
            "is_update": True,
        })



#____________ Task Archive ____________#
class TaskArchiveView(LoginRequiredMixin, View):
    def post(self, request, task_id):
        task = get_task_detail(task_id=task_id, user=request.user)

        if task is None:
            messages.error(request, "Task not found or access denied.")
            return redirect("workspaces:list")

        project_id = task.project_id

        try:
            archive_task(
                task=task,
                actor=request.user,
            )
            messages.success(request, "Task archived successfully.")

        except (ValidationError, PermissionDenied) as exc:
            messages.error(request, str(exc))

        return redirect("projects:detail", project_id=project_id)


#____________ Task Comment Create ____________#
class TaskCommentCreateView(LoginRequiredMixin, View):
    def post(self, request, task_id):
        task = get_task_detail(task_id=task_id, user=request.user)

        if task is None:
            messages.error(request, "Task not found")
            return redirect("workspaces:list")

        form = TaskCommentForm(request.POST)

        if form.is_valid():
            create_task_comment(
                task=task,
                author=request.user,
                body=form.cleaned_data["body"],
            )
            messages.success(request, "Comment added")

        return redirect("tasks:detail", task_id=task.id)


#____________ Task Attachment Upload ____________#
class TaskAttachmentUploadView(LoginRequiredMixin, View):
    def post(self, request, task_id):
        task = get_task_detail(task_id=task_id, user=request.user)

        if task is None:
            messages.error(request, "Task not found or access denied.")
            return redirect("workspaces:list")

        form = TaskAttachmentForm(request.POST, request.FILES)

        if form.is_valid():
            try:
                attach_file_to_task(
                    task=task,
                    actor=request.user,
                    uploaded_file=form.cleaned_data["file"],
                )
                messages.success(request, "File attached successfully.")

            except (ValidationError, PermissionDenied) as exc:
                messages.error(request, str(exc))

        return redirect("tasks:detail", task_id=task.id)


#____________ Task Attachment Delete ____________#
class TaskAttachmentDeleteView(LoginRequiredMixin, View):
    def post(self, request, attachment_id):
        attachment = get_object_or_404(
            TaskAttachment,
            id=attachment_id,
            task__project__workspace__memberships__user=request.user,
        )

        task_id = attachment.task_id

        try:
            delete_task_attachment(
                attachment=attachment,
                actor=request.user,
            )
            messages.success(request, "Attachment deleted successfully.")

        except (ValidationError, PermissionDenied) as exc:
            messages.error(request, str(exc))

        return redirect("tasks:detail", task_id=task_id)