from django.db import transaction

from .models import Project, Board, Column


DEFAULT_COLUMNS = [
    "Todo",
    "In Progress",
    "Review",
    "Done",
]


@transaction.atomic
def create_project(*, workspace, creator, name, description=""):
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