from django.urls import path

from .views import (
    WorkspaceArchiveAPIView,
    WorkspaceDetailAPIView,
    WorkspaceListCreateAPIView,
)

urlpatterns = [
    path("", WorkspaceListCreateAPIView.as_view(), name="workspace-list-create"),
    path("<int:workspace_id>/", WorkspaceDetailAPIView.as_view(), name="workspace-detail"),
    path("<int:workspace_id>/archive/", WorkspaceArchiveAPIView.as_view(), name="workspace-archive"),
]