from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.workspaces.selectors import (
    get_user_workspaces,
    get_workspace_detail,
)

from django.core.exceptions import PermissionDenied, ValidationError
from apps.workspaces.services import (
    create_workspace,
    update_workspace,
    archive_workspace,
    add_workspace_member,
    update_workspace_member_role,
    remove_workspace_member,
)
from .serializers import (
    WorkspaceCreateSerializer,
    WorkspaceDetailSerializer,
    WorkspaceListSerializer,
    WorkspaceUpdateSerializer,
    WorkspaceMemberSerializer,
    WorkspaceMemberAddSerializer,
    WorkspaceMemberRoleUpdateSerializer,
)

from apps.common.pagination import StandardPagination
from apps.common.api_response import success_response, error_response

from apps.workspaces.models import WorkspaceMember


class WorkspaceListCreateAPIView(APIView):
    def get(self, request):
        workspaces = get_user_workspaces(request.user)

        paginator = StandardPagination()
        page = paginator.paginate_queryset(workspaces, request)

        serializer = WorkspaceListSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = WorkspaceCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        workspace = create_workspace(
            owner=request.user,
            name=serializer.validated_data["name"],
            description=serializer.validated_data.get("description", ""),
        )

        return success_response(
            WorkspaceDetailSerializer(workspace).data,
            message="Workspace created",
            status=201,
        )

class WorkspaceDetailAPIView(APIView):
    def get(self, request, workspace_id):
        workspace = get_workspace_detail(
            workspace_id=workspace_id,
            user=request.user,
        )

        if workspace is None:
            return error_response(
                message="Workspace not found or access denied.",
                code="not_found",
                status=404,
            )

        return success_response(
            WorkspaceDetailSerializer(workspace).data,
            message="Workspace detail",
        )

    def patch(self, request, workspace_id):
        workspace = get_workspace_detail(
            workspace_id=workspace_id,
            user=request.user,
        )

        if workspace is None:
            return error_response(
                message="Workspace not found or access denied.",
                code="not_found",
                status=404,
            )

        serializer = WorkspaceUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            workspace = update_workspace(
                workspace=workspace,
                actor=request.user,
                name=serializer.validated_data["name"],
                description=serializer.validated_data.get("description", ""),
            )

        except (PermissionDenied, ValidationError) as exc:
            return error_response(
                message=str(exc),
                code="forbidden",
                status=403,
            )

        return success_response(
            WorkspaceDetailSerializer(workspace).data,
            message="Workspace Updated",
        )


class WorkspaceArchiveAPIView(APIView):
    def post(self, request, workspace_id):
        workspace = get_workspace_detail(
            workspace_id=workspace_id,
            user=request.user,
        )

        if workspace is None:
            return error_response(
                message="Workspace not found or access denied.",
                code="not_found",
                status=404,
            )

        try:
            archive_workspace(
                workspace=workspace,
                actor=request.user,
            )

        except (PermissionDenied, ValidationError) as exc:
            return error_response(
                message=str(exc),
                code = "forbidden",
                status = 403,
            )

        return success_response(
            data={"id": workspace.id},
            message="Workspace archived",
        )


class WorkspaceMemberListCreateAPIView(APIView):
    def get(self, request, workspace_id):
        workspace = get_workspace_detail(
            workspace_id=workspace_id,
            user=request.user,
        )

        if workspace is None:
            return error_response(
                message="Workspace not found or access denied.",
                code="not_found",
                status=404,
            )

        members = workspace.memberships.select_related("user").order_by("created_at")

        serializer = WorkspaceMemberSerializer(members, many=True)

        return success_response(
            serializer.data,
            message="Workspace members",
        )

    def post(self, request, workspace_id):
        workspace = get_workspace_detail(
            workspace_id=workspace_id,
            user=request.user,
        )

        if workspace is None:
            return error_response(
                message="Workspace not found or access denied.",
                code="not_found",
                status=404,
            )

        serializer = WorkspaceMemberAddSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        membership = add_workspace_member(
            workspace=workspace,
            actor=request.user,
            email=serializer.validated_data["email"],
            role=serializer.validated_data["role"],
        )

        return success_response(
            WorkspaceMemberSerializer(membership).data,
            message="Member added",
            status=201,
        )


class WorkspaceMemberUpdateDeleteAPIView(APIView):
    def patch(self, request, workspace_id, member_id):
        workspace = get_workspace_detail(
            workspace_id=workspace_id,
            user=request.user,
        )

        if workspace is None:
            return error_response(
                message="Workspace not found or access denied.",
                code="not_found",
                status=404,
            )

        serializer = WorkspaceMemberRoleUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        membership = update_workspace_member_role(
            workspace=workspace,
            actor=request.user,
            membership_id=member_id,
            new_role=serializer.validated_data["role"],
        )

        return success_response(
            WorkspaceMemberSerializer(membership).data,
            message="Member role updated",
        )

    def delete(self, request, workspace_id, member_id):
        workspace = get_workspace_detail(
            workspace_id=workspace_id,
            user=request.user,
        )

        if workspace is None:
            return error_response(
                message="Workspace not found or access denied.",
                code="not_found",
                status=404,
            )

        remove_workspace_member(
            workspace=workspace,
            actor=request.user,
            membership_id=member_id,
        )

        return success_response(
            data={"id": member_id},
            message="Member removed",
        )