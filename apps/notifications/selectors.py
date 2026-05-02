from .models import Notification


def get_user_notifications(user):
    return (
        Notification.objects
        .filter(recipient=user)
        .select_related("actor", "task")
        .order_by("-created_at")
    )


def get_unread_count(user):
    return Notification.objects.filter(
        recipient=user,
        is_read=False,
    ).count()