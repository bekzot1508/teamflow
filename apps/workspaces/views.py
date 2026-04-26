from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views import View

from .forms import WorkspaceCreateForm
from .selectors import get_user_workspaces, get_workspace_detail
from .services import create_workspace


class WorkspaceListView(LoginRequiredMixin, View):
    template_name = "workspaces/workspace_list.html"

    def get(self, request):
        workspaces = get_user_workspaces(request.user)

        return render(
            request,
            self.template_name,
            {
                "workspaces": workspaces,
            },
        )


class WorkspaceCreateView(LoginRequiredMixin, View):
    template_name = "workspaces/workspace_form.html"

    def get(self, request):
        form = WorkspaceCreateForm()

        return render(
            request,
            self.template_name,
            {
                "form": form,
            },
        )

    def post(self, request):
        form = WorkspaceCreateForm(request.POST)

        if form.is_valid():
            workspace = create_workspace(
                owner=request.user,
                name=form.cleaned_data["name"],
                description=form.cleaned_data["description"],
            )

            messages.success(request, "Workspace created successfully.")
            return redirect("workspaces:detail", workspace_id=workspace.id)

        return render(
            request,
            self.template_name,
            {
                "form": form,
            },
        )


class WorkspaceDetailView(LoginRequiredMixin, View):
    template_name = "workspaces/workspace_detail.html"

    def get(self, request, workspace_id):
        workspace = get_workspace_detail(
            workspace_id=workspace_id,
            user=request.user,
        )

        if workspace is None:
            messages.error(request, "Workspace not found or access denied.")
            return redirect("workspaces:list")

        return render(
            request,
            self.template_name,
            {
                "workspace": workspace,
            },
        )