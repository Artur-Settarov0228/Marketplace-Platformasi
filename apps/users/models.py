from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):

    class Roles(models.TextChoices):
        CUSTOMER = 'CUSTOMER', 'Customer'
        SELLER = 'SELLER', 'Seller'

    telegram_id = models.BigIntegerField(unique=True, db_index=True, null=True, blank=True)
    phone_number = models.CharField(max_length=13, blank=True)

    role = models.CharField(
        max_length=20,
        choices=Roles.choices,
        default=Roles.CUSTOMER,
        db_index=True
    )

    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        indexes = [
            models.Index(fields=['telegram_id']),
            models.Index(fields=['role']),
        ]

    def __str__(self):
        return f"{self.first_name} -{self.telegram_id} -{self.role}"