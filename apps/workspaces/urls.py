from django.urls import path

from .views import (
    WorkspaceCreateView,
    WorkspaceDetailView,
    WorkspaceListView,
)

app_name = "workspaces"

urlpatterns = [
    path("", WorkspaceListView.as_view(), name="list"),
    path("create/", WorkspaceCreateView.as_view(), name="create"),
    path("<int:workspace_id>/", WorkspaceDetailView.as_view(), name="detail"),
]