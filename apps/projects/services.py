from django.db import transaction

from .models import Project, Board, Column

from django.core.exceptions import PermissionDenied
from apps.workspaces.permissions import can_create_project


DEFAULT_COLUMNS = [
    "Todo",
    "In Progress",
    "Review",
    "Done",
]


@transaction.atomic
def create_project(*, workspace, creator, name, description=""):
    if not can_create_project(creator, workspace):
        raise PermissionDenied("You cannot create project in this workspace.")

    project = Project.objects.create(
        workspace=workspace,
        name=name,
        description=description,
        created_by=creator,
    )

    # default board
    board = Board.objects.create(
        project=project,
        name="Main Board",
    )

    # default columns
    columns = [
        Column(
            board=board,
            name=col_name,
            position=index,
        )
        for index, col_name in enumerate(DEFAULT_COLUMNS)
    ]

    Column.objects.bulk_create(columns)

    return project


@transaction.atomic
def update_project(*, project, actor, name, description=""):
    if not can_create_project(actor, project.workspace):
        raise PermissionDenied("You cannot update this project.")

    project.name = name
    project.description = description
    project.save(update_fields=["name", "description", "updated_at"])

    return project


@transaction.atomic
def archive_project(*, project, actor):
    if not can_create_project(actor, project.workspace):
        raise PermissionDenied("You cannot archive this project.")

    project.is_archived = True
    project.save(update_fields=["is_archived", "updated_at"])

    return project