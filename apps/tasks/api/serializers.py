from rest_framework import serializers

from apps.tasks.models import Task, TaskComment, TaskAttachment


class TaskListSerializer(serializers.ModelSerializer):
    assignee_email = serializers.EmailField(source="assignee.email", read_only=True)
    project_name = serializers.CharField(source="project.name", read_only=True)

    class Meta:
        model = Task
        fields = (
            "id",
            "title",
            "status",
            "priority",
            "assignee",
            "assignee_email",
            "project_name",
            "deadline",
            "created_at",
        )


class TaskDetailSerializer(serializers.ModelSerializer):
    assignee_email = serializers.EmailField(source="assignee.email", read_only=True)
    created_by_email = serializers.EmailField(source="created_by.email", read_only=True)

    class Meta:
        model = Task
        fields = "__all__"


class TaskCreateSerializer(serializers.Serializer):
    project_id = serializers.IntegerField()
    title = serializers.CharField(max_length=255)
    description = serializers.CharField(required=False, allow_blank=True)
    priority = serializers.ChoiceField(choices=Task.Priority.choices)
    assignee_id = serializers.IntegerField(required=False)
    deadline = serializers.DateTimeField(required=False)


class TaskUpdateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    description = serializers.CharField(required=False, allow_blank=True)
    priority = serializers.ChoiceField(choices=Task.Priority.choices)
    assignee_id = serializers.IntegerField(required=False, allow_null=True)
    deadline = serializers.DateTimeField(required=False, allow_null=True)


class TaskMoveSerializer(serializers.Serializer):
    column_id = serializers.IntegerField()

class TaskMoveSerializer(serializers.Serializer):
    column_id = serializers.IntegerField()
    target_position = serializers.IntegerField(required=False, min_value=0)


class TaskCommentSerializer(serializers.ModelSerializer):
    author_email = serializers.EmailField(source="author.email", read_only=True)

    class Meta:
        model = TaskComment
        fields = (
            "id",
            "task",
            "author",
            "author_email",
            "body",
            "created_at",
        )
        read_only_fields = ("id", "task", "author", "created_at")


class TaskCommentCreateSerializer(serializers.Serializer):
    body = serializers.CharField()


class TaskAttachmentSerializer(serializers.ModelSerializer):
    uploaded_by_email = serializers.EmailField(source="uploaded_by.email", read_only=True)
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = TaskAttachment
        fields = (
            "id",
            "task",
            "uploaded_by",
            "uploaded_by_email",
            "original_filename",
            "file",
            "file_url",
            "file_size",
            "created_at",
        )
        read_only_fields = (
            "id",
            "task",
            "uploaded_by",
            "original_filename",
            "file_size",
            "created_at",
        )

    def get_file_url(self, obj):
        request = self.context.get("request")

        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)

        if obj.file:
            return obj.file.url

        return None


class TaskAttachmentUploadSerializer(serializers.Serializer):
    file = serializers.FileField()