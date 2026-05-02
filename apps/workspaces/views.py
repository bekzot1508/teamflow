from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied, ValidationError
from django.shortcuts import redirect, render, get_object_or_404
from django.views import View

from .models import Workspace
from .permissions import can_manage_workspace
from .selectors import get_user_workspaces, get_workspace_detail

from .forms import (
    WorkspaceCreateForm,
    WorkspaceMemberAddForm,
    WorkspaceMemberRoleUpdateForm,
    WorkspaceUpdateForm
)
from .services import (
    create_workspace,
    add_workspace_member,
    update_workspace_member_role,
    remove_workspace_member,
    update_workspace,
    archive_workspace
)


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
                "member_add_form": WorkspaceMemberAddForm(),
                "role_update_form": WorkspaceMemberRoleUpdateForm(),
                "can_manage": can_manage_workspace(request.user, workspace),
            },
        )


class WorkspaceUpdateView(LoginRequiredMixin, View):
    template_name = "workspaces/workspace_form.html"

    def get(self, request, workspace_id):
        workspace = get_workspace_detail(workspace_id=workspace_id, user=request.user)

        if workspace is None:
            messages.error(request, "Workspace not found.")
            return redirect("workspaces:list")

        form = WorkspaceUpdateForm(instance=workspace)

        return render(request, self.template_name, {
            "form": form,
            "workspace": workspace,
            "is_update": True,
        })

    def post(self, request, workspace_id):
        workspace = get_workspace_detail(workspace_id=workspace_id, user=request.user)

        if workspace is None:
            messages.error(request, "Workspace not found.")
            return redirect("workspaces:list")

        form = WorkspaceUpdateForm(request.POST, instance=workspace)

        if form.is_valid():
            try:
                workspace = update_workspace(
                    workspace=workspace,
                    actor=request.user,
                    name=form.cleaned_data["name"],
                    description=form.cleaned_data["description"],
                )
                messages.success(request, "Workspace updated successfully.")
                return redirect("workspaces:detail", workspace_id=workspace.id)

            except PermissionDenied as exc:
                messages.error(request, str(exc))

        return render(request, self.template_name, {
            "form": form,
            "workspace": workspace,
            "is_update": True,
        })


class WorkspaceArchiveView(LoginRequiredMixin, View):
    def post(self, request, workspace_id):
        workspace = get_workspace_detail(workspace_id=workspace_id, user=request.user)

        if workspace is None:
            messages.error(request, "Workspace not found.")
            return redirect("workspaces:list")

        try:
            archive_workspace(workspace=workspace, actor=request.user)
            messages.success(request, "Workspace archived successfully.")

        except PermissionDenied as exc:
            messages.error(request, str(exc))

        return redirect("workspaces:list")


class WorkspaceMemberAddView(LoginRequiredMixin, View):
    def post(self, request, workspace_id):
        workspace = get_object_or_404(
            Workspace,
            id=workspace_id,
            memberships__user=request.user,
        )

        form = WorkspaceMemberAddForm(request.POST)

        if form.is_valid():
            try:
                add_workspace_member(
                    workspace=workspace,
                    actor=request.user,
                    email=form.cleaned_data["email"],
                    role=form.cleaned_data["role"],
                )
                messages.success(request, "Member added successfully.")

            except (ValidationError, PermissionDenied) as exc:
                messages.error(request, str(exc))

        else:
            messages.error(request, "Invalid member form data.")

        return redirect("workspaces:detail", workspace_id=workspace.id)


class WorkspaceMemberRoleUpdateView(LoginRequiredMixin, View):
    def post(self, request, workspace_id, membership_id):
        workspace = get_object_or_404(
            Workspace,
            id=workspace_id,
            memberships__user=request.user,
        )

        form = WorkspaceMemberRoleUpdateForm(request.POST)

        if form.is_valid():
            try:
                update_workspace_member_role(
                    workspace=workspace,
                    actor=request.user,
                    membership_id=membership_id,
                    new_role=form.cleaned_data["role"],
                )
                messages.success(request, "Member role updated successfully.")

            except (ValidationError, PermissionDenied) as exc:
                messages.error(request, str(exc))

        else:
            messages.error(request, "Invalid role update data.")

        return redirect("workspaces:detail", workspace_id=workspace.id)


class WorkspaceMemberRemoveView(LoginRequiredMixin, View):
    def post(self, request, workspace_id, membership_id):
        workspace = get_object_or_404(
            Workspace,
            id=workspace_id,
            memberships__user=request.user,
        )

        try:
            remove_workspace_member(
                workspace=workspace,
                actor=request.user,
                membership_id=membership_id,
            )
            messages.success(request, "Member removed successfully.")

        except (ValidationError, PermissionDenied) as exc:
            messages.error(request, str(exc))

        return redirect("workspaces:detail", workspace_id=workspace.id)