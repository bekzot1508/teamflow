from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample

from apps.projects.models import Project, Column
from apps.tasks.models import Task, TaskAttachment
from apps.tasks.selectors import (
    get_project_tasks,
    get_task_detail,
    TaskFilters,
)
from apps.tasks.services import (
    create_task,
    update_task,
    move_task_to_column,
    archive_task,
    create_task_comment,
    attach_file_to_task,
    delete_task_attachment,
)
from apps.common.api_response import success_response, error_response
from .serializers import (
    TaskListSerializer,
    TaskDetailSerializer,
    TaskCreateSerializer,
    TaskUpdateSerializer,
    TaskMoveSerializer,
    TaskCommentSerializer,
    TaskCommentCreateSerializer,
    TaskAttachmentSerializer,
    TaskAttachmentUploadSerializer,
)

from apps.common.pagination import StandardPagination

User = get_user_model()


#____________ Task List + Create ____________#
class TaskListCreateAPIView(APIView):
    def get(self, request):
        project_id = request.GET.get("project_id")

        project = get_object_or_404(
            Project,
            id=project_id,
            workspace__memberships__user=request.user,
            is_archived=False,
        )

        filters = TaskFilters(
            status=request.GET.get("status") or None,
            priority=request.GET.get("priority") or None,
            assignee_id=request.GET.get("assignee") or None,
            search=request.GET.get("search") or None,
        )

        tasks = get_project_tasks(project=project, filters=filters)

        paginator = StandardPagination()
        page = paginator.paginate_queryset(tasks, request)

        serializer = TaskListSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = TaskCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        project = get_object_or_404(
            Project,
            id=serializer.validated_data["project_id"],
            workspace__memberships__user=request.user,
            is_archived=False,
        )

        board = project.boards.first()

        if board is None:
            return error_response(
                message="Project has no board.",
                code="board_not_found",
                status=400,
            )

        column = board.columns.order_by("position").first()

        if column is None:
            return error_response(
                message="Board has no columns.",
                code="column_not_found",
                status=400,
            )

        assignee = None
        assignee_id = serializer.validated_data.get("assignee_id")

        if assignee_id:
            assignee = get_object_or_404(User, id=assignee_id)

        task = create_task(
            project=project,
            board=board,
            column=column,
            actor=request.user,
            title=serializer.validated_data["title"],
            description=serializer.validated_data.get("description", ""),
            priority=serializer.validated_data["priority"],
            assignee=assignee,
            deadline=serializer.validated_data.get("deadline"),
        )

        return success_response(
            TaskDetailSerializer(task).data,
            message="Task created",
            status=201,
        )


#____________ Task Detail ____________#
class TaskDetailAPIView(APIView):
    def get(self, request, task_id):
        task = get_task_detail(task_id=task_id, user=request.user)

        if task is None:
            return error_response(
                message="Task not found or access denied.",
                code="not_found",
                status=404,
            )

        return success_response(
            TaskDetailSerializer(task).data,
            message="Task detail",
        )


#____________ Task Update ____________#
class TaskUpdateAPIView(APIView):
    def put(self, request, task_id):
        task = get_task_detail(task_id=task_id, user=request.user)

        if task is None:
            return error_response(
                message="Task not found or access denied.",
                code="not_found",
                status=404,
            )

        serializer = TaskUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        assignee = None
        if serializer.validated_data.get("assignee_id"):
            assignee = get_object_or_404(
                User,
                id=serializer.validated_data["assignee_id"],
            )

        task = update_task(
            task=task,
            actor=request.user,
            title=serializer.validated_data["title"],
            description=serializer.validated_data.get("description", ""),
            priority=serializer.validated_data["priority"],
            assignee=assignee,
            deadline=serializer.validated_data.get("deadline"),
        )

        return success_response(
            TaskDetailSerializer(task).data,
            message="Task Updated",
        )


#____________ Task Move (KANBAN) ____________#
class TaskMoveAPIView(APIView):
    def post(self, request, task_id):
        serializer = TaskMoveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        task = get_object_or_404(Task, id=task_id)
        column = get_object_or_404(
            Column,
            id=serializer.validated_data["column_id"],
        )

        task = move_task_to_column(
            task=task,
            actor=request.user,
            target_column=column,
            target_position=serializer.validated_data.get("target_position"),
        )

        return success_response(
            TaskDetailSerializer(task).data,
            message="Task column Moved",
        )


#____________ Task Archive ____________#
class TaskArchiveAPIView(APIView):
    def post(self, request, task_id):
        task = get_task_detail(task_id=task_id, user=request.user)

        if task is None:
            return error_response(
                message="Task not found or access denied.",
                code="not_found",
                status=404,
            )

        archive_task(
            task=task,
            actor=request.user,
        )

        return success_response(
            data={"id": task.id},
            message="Task archived",
        )


class TaskCommentListCreateAPIView(APIView):
    def get(self, request, task_id):
        task = get_task_detail(task_id=task_id, user=request.user)

        if task is None:
            return error_response(
                message="Task not found or access denied.",
                code="not_found",
                status=404,
            )

        comments = task.comments.select_related("author").order_by("created_at")

        serializer = TaskCommentSerializer(comments, many=True)

        return success_response(
            serializer.data,
            message="Task comments",
        )

    def post(self, request, task_id):
        task = get_task_detail(task_id=task_id, user=request.user)

        if task is None:
            return error_response(
                message="Task not found or access denied.",
                code="not_found",
                status=404,
            )

        serializer = TaskCommentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        comment = create_task_comment(
            task=task,
            author=request.user,
            body=serializer.validated_data["body"],
        )

        return success_response(
            TaskCommentSerializer(comment).data,
            message="Comment created",
            status=201,
        )


class TaskAttachmentListUploadAPIView(APIView):
    def get(self, request, task_id):
        task = get_task_detail(task_id=task_id, user=request.user)

        if task is None:
            return error_response(
                message="Task not found or access denied.",
                code="not_found",
                status=404,
            )

        attachments = task.attachments.select_related("uploaded_by").order_by("-created_at")

        serializer = TaskAttachmentSerializer(
            attachments,
            many=True,
            context={"request": request},
        )

        return success_response(
            serializer.data,
            message="Task attachments",
        )

    def post(self, request, task_id):
        task = get_task_detail(task_id=task_id, user=request.user)

        if task is None:
            return error_response(
                message="Task not found or access denied.",
                code="not_found",
                status=404,
            )

        serializer = TaskAttachmentUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        attachment = attach_file_to_task(
            task=task,
            actor=request.user,
            uploaded_file=serializer.validated_data["file"],
        )

        return success_response(
            TaskAttachmentSerializer(
                attachment,
                context={"request": request},
            ).data,
            message="Attachment uploaded",
            status=201,
        )


class TaskAttachmentDeleteAPIView(APIView):
    def delete(self, request, attachment_id):
        attachment = get_object_or_404(
            TaskAttachment,
            id=attachment_id,
            task__project__workspace__memberships__user=request.user,
        )

        delete_task_attachment(
            attachment=attachment,
            actor=request.user,
        )

        return success_response(
            data={"id": attachment_id},
            message="Attachment deleted",
        )




# class TaskStatusUpdateAPIView(APIView):
#     def patch(self, request, task_id):
#         task = get_object_or_404(Task, id=task_id)
#
#         new_status = request.data.get("status")
#
#         change_task_status(
#             task=task,
#             actor=request.user,
#             new_status=new_status,
#         )
#
#         return success_response(
#             {
#                 "id": task.id,
#                 "status": task.status,
#             },
#             message="Status updated",
#         )