import pytest
from rest_framework.test import APIClient

from apps.notifications.models import Notification
from tests.factories import UserFactory, TaskFactory


@pytest.fixture
def auth_client():
    client = APIClient()
    user = UserFactory()
    client.force_authenticate(user=user)
    return client, user


@pytest.mark.django_db
def test_notification_list_api(auth_client):
    client, user = auth_client

    Notification.objects.create(
        recipient=user,
        type=Notification.Type.TASK_ASSIGNED,
        message="Test notification",
    )

    response = client.get("/api/v1/notifications/")

    assert response.status_code == 200
    assert response.data["success"] is True
    assert response.data["data"]["count"] == 1


@pytest.mark.django_db
def test_mark_notification_as_read_api(auth_client):
    client, user = auth_client

    notification = Notification.objects.create(
        recipient=user,
        type=Notification.Type.TASK_ASSIGNED,
        message="Unread",
    )

    response = client.post(f"/api/v1/notifications/{notification.id}/read/")

    notification.refresh_from_db()

    assert response.status_code == 200
    assert notification.is_read is True


@pytest.mark.django_db
def test_mark_all_notifications_as_read_api(auth_client):
    client, user = auth_client

    Notification.objects.create(
        recipient=user,
        type=Notification.Type.TASK_ASSIGNED,
        message="One",
    )
    Notification.objects.create(
        recipient=user,
        type=Notification.Type.STATUS_CHANGED,
        message="Two",
    )

    response = client.post("/api/v1/notifications/read-all/")

    assert response.status_code == 200
    assert Notification.objects.filter(recipient=user, is_read=False).count() == 0


@pytest.mark.django_db
def test_user_cannot_read_other_users_notification(auth_client):
    client, user = auth_client

    other_user = UserFactory()

    notification = Notification.objects.create(
        recipient=other_user,
        type=Notification.Type.TASK_ASSIGNED,
        message="Private",
    )

    response = client.post(f"/api/v1/notifications/{notification.id}/read/")

    assert response.status_code == 404