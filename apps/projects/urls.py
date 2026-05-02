from django.urls import path

from .views import ProjectCreateView, ProjectDetailView, ProjectUpdateView, ProjectArchiveView

app_name = "projects"

urlpatterns = [
    path("workspace/<int:workspace_id>/projects/create/", ProjectCreateView.as_view(), name="create"),
    path("projects/<int:project_id>/", ProjectDetailView.as_view(), name="detail"),
    path("projects/<int:project_id>/update/", ProjectUpdateView.as_view(), name="update"),
    path("projects/<int:project_id>/archive/", ProjectArchiveView.as_view(), name="archive"),
]