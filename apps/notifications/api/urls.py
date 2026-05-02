from django.urls import path

from .views import (
    NotificationListAPIView,
    NotificationReadAllAPIView,
    NotificationReadAPIView,
)

urlpatterns = [
    path("", NotificationListAPIView.as_view(), name="notification-list"),
    path("<int:notification_id>/read/", NotificationReadAPIView.as_view(), name="notification-read"),
    path("read-all/", NotificationReadAllAPIView.as_view(), name="notification-read-all"),
]