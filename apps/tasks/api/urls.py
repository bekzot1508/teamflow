from django.urls import path

from .views import (
    TaskListCreateAPIView,
    TaskDetailAPIView,
    TaskUpdateAPIView,
    TaskMoveAPIView,
    TaskArchiveAPIView,
    TaskCommentListCreateAPIView,
    TaskAttachmentListUploadAPIView,
    TaskAttachmentDeleteAPIView,
)

urlpatterns = [
    path("", TaskListCreateAPIView.as_view(), name="task-list-create"),
    path("<int:task_id>/", TaskDetailAPIView.as_view(), name="task-detail"),
    path("<int:task_id>/update/", TaskUpdateAPIView.as_view(), name="task-update"),
    path("<int:task_id>/move/", TaskMoveAPIView.as_view(), name="task-move"),
    path("<int:task_id>/archive/", TaskArchiveAPIView.as_view(), name="task-archive"),
    # path("<int:task_id>/status/", TaskStatusUpdateAPIView.as_view()),

    path("<int:task_id>/comments/", TaskCommentListCreateAPIView.as_view(), name="task-comments"),
    path("<int:task_id>/attachments/", TaskAttachmentListUploadAPIView.as_view(), name="task-attachments"),
    path("attachments/<int:attachment_id>/", TaskAttachmentDeleteAPIView.as_view(), name="task-attachment-delete"),
]