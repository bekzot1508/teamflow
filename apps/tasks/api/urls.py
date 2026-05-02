from django.urls import path

from .views import (
    TaskListCreateAPIView,
    TaskDetailAPIView,
    TaskUpdateAPIView,
    TaskMoveAPIView,
    TaskArchiveAPIView,
)

urlpatterns = [
    path("", TaskListCreateAPIView.as_view(), name="task-list-create"),
    path("<int:task_id>/", TaskDetailAPIView.as_view(), name="task-detail"),
    path("<int:task_id>/update/", TaskUpdateAPIView.as_view(), name="task-update"),
    path("<int:task_id>/move/", TaskMoveAPIView.as_view(), name="task-move"),
    path("<int:task_id>/archive/", TaskArchiveAPIView.as_view(), name="task-archive"),
]