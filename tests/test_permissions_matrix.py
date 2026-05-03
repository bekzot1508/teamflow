import pytest
from django.core.exceptions import PermissionDenied

from apps.tasks.services import create_task
from apps.workspaces.models import WorkspaceMember
from tests.factories import (
    UserFactory,
    WorkspaceFactory,
    WorkspaceMemberFactory,
    ProjectFactory,
    BoardFactory,
    ColumnFactory,
)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "role,should_pass",
    [
        (WorkspaceMember.Role.OWNER, True),
        (WorkspaceMember.Role.ADMIN, True),
        (WorkspaceMember.Role.MEMBER, True),
        (WorkspaceMember.Role.VIEWER, False),
    ],
)
def test_create_task_permission_matrix(role, should_pass):
    user = UserFactory()
    workspace = WorkspaceFactory()

    WorkspaceMemberFactory(
        workspace=workspace,
        user=user,
        role=role,
    )

    project = ProjectFactory(workspace=workspace, created_by=user)
    board = BoardFactory(project=project)
    column = ColumnFactory(board=board)

    if should_pass:
        create_task(
            project=project,
            board=board,
            column=column,
            actor=user,
            title="Matrix task",
        )
    else:
        with pytest.raises(PermissionDenied):
            create_task(
                project=project,
                board=board,
                column=column,
                actor=user,
                title="Forbidden",
            )