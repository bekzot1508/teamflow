from rest_framework import serializers

from apps.projects.models import Project, Board, Column


class ColumnSerializer(serializers.ModelSerializer):
    class Meta:
        model = Column
        fields = (
            "id",
            "name",
            "position",
        )


class BoardSerializer(serializers.ModelSerializer):
    columns = ColumnSerializer(many=True, read_only=True)

    class Meta:
        model = Board
        fields = (
            "id",
            "name",
            "columns",
        )


class ProjectListSerializer(serializers.ModelSerializer):
    workspace_name = serializers.CharField(source="workspace.name", read_only=True)
    created_by_email = serializers.EmailField(source="created_by.email", read_only=True)

    class Meta:
        model = Project
        fields = (
            "id",
            "workspace",
            "workspace_name",
            "name",
            "slug",
            "description",
            "created_by_email",
            "is_archived",
            "created_at",
        )


class ProjectDetailSerializer(serializers.ModelSerializer):
    workspace_name = serializers.CharField(source="workspace.name", read_only=True)
    created_by_email = serializers.EmailField(source="created_by.email", read_only=True)
    boards = BoardSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = (
            "id",
            "workspace",
            "workspace_name",
            "name",
            "slug",
            "description",
            "created_by_email",
            "is_archived",
            "boards",
            "created_at",
            "updated_at",
        )


class ProjectCreateSerializer(serializers.Serializer):
    workspace_id = serializers.IntegerField()
    name = serializers.CharField(max_length=255)
    description = serializers.CharField(required=False, allow_blank=True)


class ProjectUpdateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    description = serializers.CharField(required=False, allow_blank=True)