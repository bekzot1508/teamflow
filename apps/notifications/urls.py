from django.urls import path

from .views import (
    NotificationListView,
    NotificationReadView,
    NotificationReadAllView,
)

app_name = "notifications"

urlpatterns = [
    path("", NotificationListView.as_view(), name="list"),
    path("<int:notification_id>/read/", NotificationReadView.as_view(), name="read"),
    path("read-all/", NotificationReadAllView.as_view(), name="read_all"),
]