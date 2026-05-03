import pytest

from apps.workspaces.services import archive_workspace
from apps.workspaces.selectors import get_user_workspaces, get_workspace_detail
from apps.workspaces.models import WorkspaceMember
from tests.factories import UserFactory, WorkspaceFactory, WorkspaceMemberFactory


@pytest.mark.django_db
def test_archive_workspace_hides_from_list():
    owner = UserFactory()
    workspace = WorkspaceFactory(owner=owner)

    WorkspaceMemberFactory(
        workspace=workspace,
        user=owner,
        role=WorkspaceMember.Role.OWNER,
    )

    archive_workspace(workspace=workspace, actor=owner)

    workspaces = get_user_workspaces(owner)

    assert workspace not in list(workspaces)


@pytest.mark.django_db
def test_archived_workspace_detail_returns_none():
    owner = UserFactory()
    workspace = WorkspaceFactory(owner=owner)

    WorkspaceMemberFactory(
        workspace=workspace,
        user=owner,
        role=WorkspaceMember.Role.OWNER,
    )

    archive_workspace(workspace=workspace, actor=owner)

    result = get_workspace_detail(
        workspace_id=workspace.id,
        user=owner,
    )

    assert result is None


@pytest.mark.django_db
def test_non_owner_cannot_archive_workspace():
    owner = UserFactory()
    member = UserFactory()

    workspace = WorkspaceFactory(owner=owner)

    WorkspaceMemberFactory(
        workspace=workspace,
        user=owner,
        role=WorkspaceMember.Role.OWNER,
    )
    WorkspaceMemberFactory(
        workspace=workspace,
        user=member,
        role=WorkspaceMember.Role.ADMIN,
    )

    with pytest.raises(Exception):
        archive_workspace(workspace=workspace, actor=member)