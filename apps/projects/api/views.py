from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied, ValidationError

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


from apps.workspaces.models import Workspace
from apps.workspaces.permissions import can_create_project
from apps.projects.selectors import (
    get_project_detail,
    get_user_projects,
)

from apps.projects.services import (
    create_project,
    update_project,
    archive_project,
)

from .serializers import (
    ProjectCreateSerializer,
    ProjectDetailSerializer,
    ProjectListSerializer,
    ProjectUpdateSerializer,
)

from apps.common.pagination import StandardPagination
from apps.common.api_response import success_response, error_response


class ProjectListCreateAPIView(APIView):
    def get(self, request):
        projects = get_user_projects(request.user)

        paginator = StandardPagination()
        page = paginator.paginate_queryset(projects, request)

        serializer = ProjectListSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = ProjectCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        workspace = get_object_or_404(
            Workspace,
            id=serializer.validated_data["workspace_id"],
            memberships__user=request.user,
            is_archived=False,
        )

        if not can_create_project(request.user, workspace):
            raise PermissionDenied("You do not have permission to create project.")

        project = create_project(
            workspace=workspace,
            creator=request.user,
            name=serializer.validated_data["name"],
            description=serializer.validated_data.get("description", ""),
        )

        return success_response(
            ProjectDetailSerializer(project).data,
            message="Project created",
            status=201,
        )


class ProjectDetailAPIView(APIView):
    def get(self, request, project_id):
        project = get_project_detail(
            project_id=project_id,
            user=request.user,
        )

        if project is None:
            return error_response(
                message="Project not found or access denied.",
                code="not_found",
                status=404,
            )

        return success_response(
            WorkspaceDetailSerializer(project).data,
            message="project detail",
        )

    def patch(self, request, project_id):
        project = get_project_detail(
            project_id=project_id,
            user=request.user,
        )

        if project is None:
            return error_response(
                message="Project not found or access denied.",
                code="not_found",
                status=404,
            )

        serializer = ProjectUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            project = update_project(
                project=project,
                actor=request.user,
                name=serializer.validated_data["name"],
                description=serializer.validated_data.get("description", ""),
            )

        except (PermissionDenied, ValidationError) as exc:
            return error_response(
                message=str(exc),
                code="Forbidden",
                status=403,
            )

        return success_response(
            WorkspaceDetailSerializer(project).data,
            message="project Updated",
        )


class ProjectArchiveAPIView(APIView):
    def post(self, request, project_id):
        project = get_project_detail(
            project_id=project_id,
            user=request.user,
        )

        if project is None:
            return error_response(
                message="Project not found or access denied.",
                code="not_found",
                status=404,
            )

        try:
            archive_project(
                project=project,
                actor=request.user,
            )

        except (PermissionDenied, ValidationError) as exc:
            return error_response(
                message=str(exc),
                code = "Forbidden",
                status = 403,
            )

        return success_response(
            data={"id": project.id},
            message="project archived",
        )