from .selectors import get_unread_count


def unread_notifications(request):
    if not request.user.is_authenticated:
        return {
            "unread_notifications_count": 0,
        }

    return {
        "unread_notifications_count": get_unread_count(request.user),
    }