import pytest
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


@pytest.mark.django_db
def test_attach_file_to_task_success():
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

    uploaded_file = SimpleUploadedFile(
        "test.txt",
        b"hello world",
        content_type="text/plain",
    )

    attachment = attach_file_to_task(
        task=task,
        actor=user,
        uploaded_file=uploaded_file,
    )

    assert attachment.task == task
    assert attachment.uploaded_by == user
    assert attachment.original_filename == "test.txt"