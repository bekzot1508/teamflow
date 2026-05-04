from django.urls import path

from .views import (
    WorkspaceArchiveAPIView,
    WorkspaceDetailAPIView,
    WorkspaceListCreateAPIView,
    WorkspaceMemberListCreateAPIView,
    WorkspaceMemberUpdateDeleteAPIView,
)

urlpatterns = [
    path("", WorkspaceListCreateAPIView.as_view(), name="workspace-list-create"),
    path("<int:workspace_id>/", WorkspaceDetailAPIView.as_view(), name="workspace-detail"),
    path("<int:workspace_id>/archive/", WorkspaceArchiveAPIView.as_view(), name="workspace-archive"),

    path("<int:workspace_id>/members/", WorkspaceMemberListCreateAPIView.as_view(), name="workspace-members"),
    path("<int:workspace_id>/members/<int:member_id>/", WorkspaceMemberUpdateDeleteAPIView.as_view(), name="workspace-member-detail"),
]