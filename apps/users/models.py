from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):

    class Roles(models.TextChoices):
        CUSTOMER = "customer", "Xaridor"
        SELLER = "seller", "Sotuvchi"

    telegram_id = models.BigIntegerField(
        unique=True,
        db_index=True
    )

    username = models.CharField(
        max_length=150,
        unique=True
    )

    first_name = models.CharField(
        max_length=150
    )

    last_name = models.CharField(
        max_length=150,
        blank=True
    )

    phone_number = models.CharField(
        max_length=20,
        blank=True
    )

    role = models.CharField(
        max_length=20,
        choices=Roles.choices,
        default=Roles.CUSTOMER,
        db_index=True
    )

    avatar = models.ImageField(
        upload_to="avatars/",
        blank=True,
        null=True
    )

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.username} ({self.role})"