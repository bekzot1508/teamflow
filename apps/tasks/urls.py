from django.urls import path
from .views import (
    TaskCreateView,
    TaskDetailView,
    TaskMoveView,
    TaskUpdateView,
    TaskArchiveView,
    TaskCommentCreateView,
    TaskAttachmentUploadView,
    TaskAttachmentDeleteView,
)

app_name = "tasks"

urlpatterns = [
    path("project/<int:project_id>/tasks/create/", TaskCreateView.as_view(), name="create"),
    path("tasks/<int:task_id>/", TaskDetailView.as_view(), name="detail"),
    path("tasks/<int:task_id>/move/",  TaskMoveView.as_view(), name="move"),
    path("tasks/<int:task_id>/update/", TaskUpdateView.as_view(), name="update"),
    path("tasks/<int:task_id>/archive/", TaskArchiveView.as_view(), name="archive"),
    path("tasks/<int:task_id>/comments/", TaskCommentCreateView.as_view(), name="comment_create"),
    path("tasks/<int:task_id>/attachments/upload/", TaskAttachmentUploadView.as_view(), name="attachment_upload"),
    path("attachments/<int:attachment_id>/delete/", TaskAttachmentDeleteView.as_view(), name="attachment_delete"),
]