from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View

from apps.workspaces.models import Workspace
from .selectors import get_project_detail
from apps.tasks.selectors import get_project_tasks, TaskFilters
from apps.workspaces.permissions import can_create_project
from .forms import ProjectCreateForm, ProjectUpdateForm
from .services import create_project, update_project, archive_project


#______________ Project Create ______________
class ProjectCreateView(LoginRequiredMixin, View):
    template_name = "projects/project_form.html"

    def get(self, request, workspace_id):
        workspace = get_object_or_404(Workspace, id=workspace_id)

        if not can_create_project(request.user, workspace):
            messages.error(request, "Permission denied")
            return redirect("workspaces:detail", workspace_id=workspace.id)

        return render(request, self.template_name, {
            "form": ProjectCreateForm(),
            "workspace": workspace,
        })

    def post(self, request, workspace_id):
        workspace = get_object_or_404(Workspace, id=workspace_id)

        if not can_create_project(request.user, workspace):
            messages.error(request, "Permission denied")
            return redirect("workspaces:detail", workspace_id=workspace.id)

        form = ProjectCreateForm(request.POST)

        if form.is_valid():
            project = create_project(
                workspace=workspace,
                creator=request.user,
                name=form.cleaned_data["name"],
                description=form.cleaned_data["description"],
            )

            messages.success(request, "Project created successfully")
            return redirect("projects:detail", project_id=project.id)

        return render(request, self.template_name, {
            "form": form,
            "workspace": workspace,
        })


class ProjectDetailView(LoginRequiredMixin, View):
    template_name = "projects/project_detail.html"

    def get(self, request, project_id):
        project = get_project_detail(
            project_id=project_id,
            user=request.user,
        )

        if project is None:
            messages.error(request, "Project not found or access denied.")
            return redirect("workspaces:list")

        filters = TaskFilters(
            status=request.GET.get("status") or None,
            priority=request.GET.get("priority") or None,
            assignee_id=request.GET.get("assignee") or None,
            search=request.GET.get("search") or None,
        )

        tasks = get_project_tasks(project=project, filters=filters)

        return render(
            request,
            self.template_name,
            {
                "project": project,
                "workspace": project.workspace,
                "tasks": tasks,
            },
        )


class ProjectUpdateView(LoginRequiredMixin, View):
    template_name = "projects/project_form.html"

    def get(self, request, project_id):
        project = get_project_detail(project_id=project_id, user=request.user)

        if project is None:
            messages.error(request, "Project not found.")
            return redirect("workspaces:list")

        form = ProjectUpdateForm(instance=project)

        return render(request, self.template_name, {
            "form": form,
            "workspace": project.workspace,
            "project": project,
            "is_update": True,
        })

    def post(self, request, project_id):
        project = get_project_detail(project_id=project_id, user=request.user)

        if project is None:
            messages.error(request, "Project not found.")
            return redirect("workspaces:list")

        form = ProjectUpdateForm(request.POST, instance=project)

        if form.is_valid():
            try:
                project = update_project(
                    project=project,
                    actor=request.user,
                    name=form.cleaned_data["name"],
                    description=form.cleaned_data["description"],
                )
                messages.success(request, "Project updated successfully.")
                return redirect("projects:detail", project_id=project.id)

            except PermissionDenied as exc:
                messages.error(request, str(exc))

        return render(request, self.template_name, {
            "form": form,
            "workspace": project.workspace,
            "project": project,
            "is_update": True,
        })


class ProjectArchiveView(LoginRequiredMixin, View):
    def post(self, request, project_id):
        project = get_project_detail(project_id=project_id, user=request.user)

        if project is None:
            messages.error(request, "Project not found.")
            return redirect("workspaces:list")

        workspace_id = project.workspace_id

        try:
            archive_project(project=project, actor=request.user)
            messages.success(request, "Project archived successfully.")

        except PermissionDenied as exc:
            messages.error(request, str(exc))

        return redirect("workspaces:detail", workspace_id=workspace_id)