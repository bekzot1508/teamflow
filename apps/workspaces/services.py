from django.db import transaction

from .models import Workspace, WorkspaceMember


@transaction.atomic
def create_workspace(*, owner, name, description=""):
    workspace = Workspace.objects.create(
        owner=owner,
        name=name,
        description=description,
    )

    WorkspaceMember.objects.create(
        workspace=workspace,
        user=owner,
        role=WorkspaceMember.Role.OWNER,
    )

    return workspace