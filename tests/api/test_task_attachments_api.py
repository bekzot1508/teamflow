import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient

from apps.tasks.models import TaskAttachment
from apps.workspaces.models import WorkspaceMember
from tests.factories import (
    UserFactory,
    WorkspaceFactory,
    WorkspaceMemberFactory,
    ProjectFactory,
    BoardFactory,
    ColumnFactory,
    TaskFactory,
)


@pytest.fixture
def task_attachment_api_setup():
    client = APIClient()

    owner = UserFactory()

    workspace = WorkspaceFactory(owner=owner)
    WorkspaceMemberFactory(workspace=workspace, user=owner, role=WorkspaceMember.Role.OWNER)

    project = ProjectFactory(workspace=workspace, created_by=owner)
    board = BoardFactory(project=project)
    column = ColumnFactory(board=board, name="Todo", position=0)

    task = TaskFactory(project=project, board=board, column=column, created_by=owner)

    client.force_authenticate(user=owner)

    return client, owner, task


@pytest.mark.django_db
def test_task_attachment_upload_api(task_attachment_api_setup):
    client, owner, task = task_attachment_api_setup

    uploaded_file = SimpleUploadedFile(
        "test.txt",
        b"hello world",
        content_type="text/plain",
    )

    response = client.post(
        f"/api/v1/tasks/{task.id}/attachments/",
        {"file": uploaded_file},
        format="multipart",
    )

    assert response.status_code == 201
    assert TaskAttachment.objects.filter(task=task, uploaded_by=owner).exists()


@pytest.mark.django_db
def test_task_attachment_invalid_file_api(task_attachment_api_setup):
    client, owner, task = task_attachment_api_setup

    uploaded_file = SimpleUploadedFile(
        "bad.exe",
        b"bad file",
        content_type="application/octet-stream",
    )

    response = client.post(
        f"/api/v1/tasks/{task.id}/attachments/",
        {"file": uploaded_file},
        format="multipart",
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_task_attachment_delete_api(task_attachment_api_setup):
    client, owner, task = task_attachment_api_setup

    uploaded_file = SimpleUploadedFile(
        "test.txt",
        b"hello world",
        content_type="text/plain",
    )

    attachment = TaskAttachment.objects.create(
        task=task,
        uploaded_by=owner,
        file=uploaded_file,
        original_filename="test.txt",
        file_size=uploaded_file.size,
    )

    response = client.delete(
        f"/api/v1/tasks/attachments/{attachment.id}/",
    )

    assert response.status_code == 200
    assert not TaskAttachment.objects.filter(id=attachment.id).exists()