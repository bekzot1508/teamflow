from rest_framework import serializers

from apps.notifications.models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    actor_email = serializers.EmailField(source="actor.email", read_only=True)
    task_title = serializers.CharField(source="task.title", read_only=True)

    class Meta:
        model = Notification
        fields = (
            "id",
            "type",
            "message",
            "is_read",
            "actor",
            "actor_email",
            "task",
            "task_title",
            "created_at",
        )