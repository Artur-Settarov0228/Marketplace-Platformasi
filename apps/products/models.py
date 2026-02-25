from django.db import models
from django.conf import settings


class Product(models.Model):

    class Status(models.TextChoices):
        MODERATION = 'MODERATION', 'Moderation'
        ACTIVE = 'ACTIVE', 'Active'
        SOLD = 'SOLD', 'Sold'
        ARCHIVED = 'ARCHIVED', 'Archived'

    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='products'
    )

    category = models.ForeignKey(
        'categories.Category',
        on_delete=models.PROTECT,
        related_name='products'
    )

    title = models.CharField(max_length=200)
    description = models.TextField()

    price = models.DecimalField(max_digits=12, decimal_places=2, db_index=True)

    region = models.CharField(max_length=100, db_index=True)

    view_count = models.PositiveIntegerField(default=0)
    favorite_count = models.PositiveIntegerField(default=0)

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.MODERATION,
        db_index=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['price']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return self.title