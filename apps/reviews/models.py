from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.orders.models import Order


class Review(models.Model):

    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name="review"
    )

    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="written_reviews"
    )

    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="received_reviews"
    )

    rating = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5)
        ]
    )

    comment = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["seller"]),
        ]

    def save(self, *args, **kwargs):
        if self.order.status != self.order.Status.COMPLETED:
            raise ValueError("Faqat yakunlangan buyurtmaga review yozish mumkin")

        if self.reviewer != self.order.buyer:
            raise ValueError("Faqat buyer review yozishi mumkin")

        if self.seller != self.order.seller:
            raise ValueError("Seller notogri")

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.reviewer} → {self.seller} ({self.rating}/5)"