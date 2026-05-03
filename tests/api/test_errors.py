import pytest
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_task_create_invalid_data():
    client = APIClient()

    response = client.post(
        "/api/v1/tasks/",
        {},
        format="json",
    )

    assert response.status_code in [400, 401]