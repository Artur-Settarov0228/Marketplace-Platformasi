from django.db import models
from django.utils.text import slugify


class Category(models.Model):

    name = models.CharField(max_length=255)

    slug = models.SlugField(unique=True, blank=True)

    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children"
    )

    icon = models.ImageField(
        upload_to="categories/icons/",
        blank=True
    )

    description = models.TextField(blank=True)

    is_active = models.BooleanField(default=True)

    order_num = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order_num", "name"]

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):

        if not self.slug:
            self.slug = slugify(self.name)

        super().save(*args, **kwargs)