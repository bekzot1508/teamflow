import pytest
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.tasks.services import attach_file_to_task
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
def attachment_setup():
    user = UserFactory()
    workspace = WorkspaceFactory(owner=user)

    WorkspaceMemberFactory(
        workspace=workspace,
        user=user,
        role=WorkspaceMember.Role.OWNER,
    )

    project = ProjectFactory(workspace=workspace, created_by=user)
    board = BoardFactory(project=project)
    column = ColumnFactory(board=board)

    task = TaskFactory(
        project=project,
        board=board,
        column=column,
        created_by=user,
    )

    return user, task


@pytest.mark.django_db
def test_reject_invalid_file_extension(attachment_setup):
    user, task = attachment_setup

    uploaded_file = SimpleUploadedFile(
        "bad.exe",
        b"fake exe content",
        content_type="application/octet-stream",
    )

    with pytest.raises(ValidationError):
        attach_file_to_task(
            task=task,
            actor=user,
            uploaded_file=uploaded_file,
        )


@pytest.mark.django_db
def test_reject_large_file(attachment_setup):
    user, task = attachment_setup

    uploaded_file = SimpleUploadedFile(
        "large.txt",
        b"a" * (6 * 1024 * 1024),
        content_type="text/plain",
    )

    with pytest.raises(ValidationError):
        attach_file_to_task(
            task=task,
            actor=user,
            uploaded_file=uploaded_file,
        )