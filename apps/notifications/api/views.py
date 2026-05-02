from django.shortcuts import get_object_or_404

from rest_framework.response import Response
from rest_framework.views import APIView

from apps.notifications.models import Notification
from apps.notifications.selectors import get_user_notifications
from apps.notifications.services import (
    mark_all_notifications_as_read,
    mark_notification_as_read,
)

from .serializers import NotificationSerializer
from apps.common.pagination import StandardPagination
from apps.common.api_response import success_response, error_response


class NotificationListAPIView(APIView):
    def get(self, request):
        notifications = get_user_notifications(request.user)

        paginator = StandardPagination()
        page = paginator.paginate_queryset(notifications, request)

        serializer = NotificationSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


class NotificationReadAPIView(APIView):
    def post(self, request, notification_id):
        notification = get_object_or_404(
            Notification,
            id=notification_id,
            recipient=request.user,
        )

        mark_notification_as_read(
            notification=notification,
            user=request.user,
        )

        return success_response(
            data={"id": notification.id},
            message="notification marked as read",
        )


class NotificationReadAllAPIView(APIView):
    def post(self, request):
        mark_all_notifications_as_read(user=request.user)

        return success_response(
            message="all notification marked as read",
        )