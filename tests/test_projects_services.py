import pytest
from django.core.exceptions import PermissionDenied

from apps.projects.services import create_project, archive_project
from apps.workspaces.models import WorkspaceMember
from tests.factories import UserFactory, WorkspaceFactory, WorkspaceMemberFactory


@pytest.mark.django_db
def test_create_project_success():
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
        name="New Project",
        description="Test",
    )

    assert project.name == "New Project"
    assert project.workspace == workspace


@pytest.mark.django_db
def test_viewer_cannot_create_project():
    viewer = UserFactory()
    workspace = WorkspaceFactory()

    WorkspaceMemberFactory(
        workspace=workspace,
        user=viewer,
        role=WorkspaceMember.Role.VIEWER,
    )

    with pytest.raises(PermissionDenied):
        create_project(
            workspace=workspace,
            creator=viewer,
            name="Forbidden",
        )


@pytest.mark.django_db
def test_archive_project():
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
        name="To Archive",
    )
    archive_project(project=project, actor=owner)

    project.refresh_from_db()
    assert project.is_archived is True