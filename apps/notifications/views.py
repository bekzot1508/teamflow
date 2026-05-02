from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View

from .selectors import get_user_notifications
from .services import (
    mark_notification_as_read,
    mark_all_notifications_as_read,
)
from .models import Notification


class NotificationListView(LoginRequiredMixin, View):
    template_name = "notifications/list.html"

    def get(self, request):
        notifications = get_user_notifications(request.user)

        return render(request, self.template_name, {
            "notifications": notifications,
        })


class NotificationReadView(LoginRequiredMixin, View):
    def post(self, request, notification_id):
        notification = get_object_or_404(Notification, id=notification_id)

        mark_notification_as_read(
            notification=notification,
            user=request.user,
        )

        return redirect("notifications:list")


class NotificationReadAllView(LoginRequiredMixin, View):
    def post(self, request):
        mark_all_notifications_as_read(user=request.user)

        return redirect("notifications:list")