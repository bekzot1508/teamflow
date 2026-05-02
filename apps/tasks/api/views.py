from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample

from apps.projects.models import Project, Column
from apps.tasks.models import Task
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
)

User = get_user_model()

from .serializers import (
    TaskListSerializer,
    TaskDetailSerializer,
    TaskCreateSerializer,
    TaskUpdateSerializer,
    TaskMoveSerializer,
)

from apps.common.pagination import StandardPagination
from apps.common.api_response import success_response, error_response

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