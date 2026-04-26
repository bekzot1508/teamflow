from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import BaseUserManager
from django.db import models
from apps.common.models import TimeStampedModel


#_______________User Manager_____________
class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email required")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)

        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(email, password, **extra_fields)


#_______________User_____________
class User(AbstractUser, TimeStampedModel):
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)

    avatar = models.ImageField(
        upload_to="avatars/",
        blank=True,
        null=True,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    objects = UserManager()

    def __str__(self):
        return self.email