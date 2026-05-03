import pytest

from apps.projects.services import create_project, archive_project
from apps.projects.selectors import get_user_projects, get_project_detail
from apps.workspaces.models import WorkspaceMember
from tests.factories import UserFactory, WorkspaceFactory, WorkspaceMemberFactory


@pytest.mark.django_db
def test_archive_project_hides_from_project_list():
    owner = UserFactory()
    workspace = WorkspaceFactory(owner=owner)

    WorkspaceMemberFactory(
        workspace=workspace,
        user=owner,
        role=WorkspaceMember.Role.OWNER,
    )

    project = create_project(
        workspace=workspace,
        creator=owner,
        name="Archived Project",
        description="Test",
    )

    archive_project(project=project, actor=owner)

    projects = get_user_projects(owner)

    assert project not in list(projects)


@pytest.mark.django_db
def test_archived_project_detail_returns_none():
    owner = UserFactory()
    workspace = WorkspaceFactory(owner=owner)

    WorkspaceMemberFactory(
        workspace=workspace,
        user=owner,
        role=WorkspaceMember.Role.OWNER,
    )

    project = create_project(
        workspace=workspace,
        creator=owner,
        name="Archived Project",
        description="Test",
    )

    archive_project(project=project, actor=owner)

    result = get_project_detail(
        project_id=project.id,
        user=owner,
    )

    assert result is None


@pytest.mark.django_db
def test_project_creation_creates_board_and_columns():
    owner = UserFactory()
    workspace = WorkspaceFactory(owner=owner)

    WorkspaceMemberFactory(
        workspace=workspace,
        user=owner,
        role=WorkspaceMember.Role.OWNER,
    )

    project = create_project(
        workspace=workspace,
        creator=owner,
        name="Project With Board",
        description="Test",
    )

    board = project.boards.first()

    assert board is not None
    assert board.columns.count() == 4
    assert list(board.columns.order_by("position").values_list("name", flat=True)) == [
        "Todo",
        "In Progress",
        "Review",
        "Done",
    ]