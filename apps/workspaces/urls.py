from django.urls import path

from .views import (
    WorkspaceCreateView,
    WorkspaceDetailView,
    WorkspaceListView,
    WorkspaceUpdateView,
    WorkspaceArchiveView,
    WorkspaceMemberAddView,
    WorkspaceMemberRoleUpdateView,
    WorkspaceMemberRemoveView,
)

app_name = "workspaces"

urlpatterns = [
    path("", WorkspaceListView.as_view(), name="list"),
    path("create/", WorkspaceCreateView.as_view(), name="create"),
    path("<int:workspace_id>/", WorkspaceDetailView.as_view(), name="detail"),
    path("<int:workspace_id>/update/", WorkspaceUpdateView.as_view(), name="update"),
    path("<int:workspace_id>/archive/", WorkspaceArchiveView.as_view(), name="archive"),

    path("<int:workspace_id>/members/add/", WorkspaceMemberAddView.as_view(), name="member_add"),
    path("<int:workspace_id>/members/<int:membership_id>/role/", WorkspaceMemberRoleUpdateView.as_view(), name="member_role_update"),
    path("<int:workspace_id>/members/<int:membership_id>/remove/", WorkspaceMemberRemoveView.as_view(), name="member_remove"),
]