from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View

from apps.workspaces.models import Workspace
from apps.workspaces.permissions import can_create_project

from .forms import ProjectCreateForm
from .services import create_project

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