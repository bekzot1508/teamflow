from django.conf import settings
from django.db import models
from django.utils.text import slugify

from apps.common.models import TimeStampedModel
from apps.workspaces.models import Workspace


#____________ Project ____________
class Project(TimeStampedModel):
    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name="projects",
    )

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)

    description = models.TextField(blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_projects",
    )

    is_archived = models.BooleanField(default=False)

    class Meta:
        unique_together = ("workspace", "slug")
        ordering = ("-created_at",)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

        super().save(*args, **kwargs)


#____________ Board ____________
class Board(TimeStampedModel):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="boards",
    )

    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


#____________ Column ____________
class Column(TimeStampedModel):
    board = models.ForeignKey(
        Board,
        on_delete=models.CASCADE,
        related_name="columns",
    )

    name = models.CharField(max_length=100)
    position = models.PositiveIntegerField()

    class Meta:
        ordering = ("position",)

    def __str__(self):
        return f"{self.board.name} - {self.name}"