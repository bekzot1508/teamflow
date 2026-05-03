import factory
from django.contrib.auth import get_user_model
from django.utils.text import slugify

from apps.workspaces.models import Workspace, WorkspaceMember
from apps.projects.models import Project, Board, Column
from apps.tasks.models import Task

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ("email",)

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    username = factory.Sequence(lambda n: f"user{n}")
    full_name = factory.Sequence(lambda n: f"User {n}")
    password = factory.PostGenerationMethodCall("set_password", "password123")


class WorkspaceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Workspace

    name = factory.Sequence(lambda n: f"Workspace {n}")
    slug = factory.LazyAttribute(lambda obj: slugify(obj.name))
    description = "Test workspace"
    owner = factory.SubFactory(UserFactory)


class WorkspaceMemberFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = WorkspaceMember

    workspace = factory.SubFactory(WorkspaceFactory)
    user = factory.SubFactory(UserFactory)
    role = WorkspaceMember.Role.MEMBER


class ProjectFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Project

    workspace = factory.SubFactory(WorkspaceFactory)
    name = factory.Sequence(lambda n: f"Project {n}")
    slug = factory.LazyAttribute(lambda obj: slugify(obj.name))
    description = "Test project"
    created_by = factory.SubFactory(UserFactory)


class BoardFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Board

    project = factory.SubFactory(ProjectFactory)
    name = "Main Board"


class ColumnFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Column

    board = factory.SubFactory(BoardFactory)
    name = "Todo"
    position = 0


class TaskFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Task

    project = factory.SubFactory(ProjectFactory)
    board = factory.SubFactory(BoardFactory)
    column = factory.SubFactory(ColumnFactory)
    title = factory.Sequence(lambda n: f"Task {n}")
    description = "Test task"
    priority = Task.Priority.MEDIUM
    status = Task.Status.TODO
    created_by = factory.SubFactory(UserFactory)
    position = 0