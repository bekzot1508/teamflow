from rest_framework import serializers

from apps.tasks.models import Task


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