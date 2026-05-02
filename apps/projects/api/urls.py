from django.urls import path

from .views import (
    ProjectArchiveAPIView,
    ProjectDetailAPIView,
    ProjectListCreateAPIView,
)

urlpatterns = [
    path("", ProjectListCreateAPIView.as_view(), name="project-list-create"),
    path("<int:project_id>/", ProjectDetailAPIView.as_view(), name="project-detail"),
    path("<int:project_id>/archive/", ProjectArchiveAPIView.as_view(), name="project-archive"),
]