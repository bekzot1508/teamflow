import pytest
from rest_framework.test import APIClient

from django.contrib.auth import get_user_model

from tests.factories import UserFactory

User = get_user_model()

@pytest.mark.django_db
def test_user_me_api():
    client = APIClient()
    user = UserFactory(email="me@example.com")
    client.force_authenticate(user=user)

    response = client.get("/api/v1/users/me/")

    assert response.status_code == 200

    data = response.data.get("data", response.data)

    assert data["email"] == "me@example.com"


@pytest.mark.django_db
def test_user_register_api():
    client = APIClient()

    response = client.post(
        "/api/v1/users/register/",
        {
            "email": "new@example.com",
            "username": "newuser",
            "full_name": "New User",
            "password": "strongpass123",
        },
        format="json",
    )

    assert response.status_code == 201
    assert User.objects.filter(email="new@example.com").exists()