from django.db import models
from apps.users.models import User
from apps.categories.models import Category


class Product(models.Model):

    class Condition(models.TextChoices):
        NEW = "new", "Yangi"
        IDEAL = "ideal", "Ideal"
        GOOD = "good", "Yaxshi"
        FAIR = "fair", "Qoniqarli"


    class PriceType(models.TextChoices):
        FIXED = "fixed", "Qat'iy"
        NEGOTIABLE = "negotiable", "Kelishiladi"
        FREE = "free", "Bepul"
        EXCHANGE = "exchange", "Ayirboshlash"


    class Status(models.TextChoices):
        MODERATION = "moderation", "Moderatsiyada"
        ACTIVE = "active", "Aktiv"
        REJECTED = "rejected", "Rad etilgan"
        SOLD = "sold", "Sotilgan"
        ARCHIVED = "archived", "Arxivlangan"


    seller = models.ForeignKey(User,on_delete=models.CASCADE,related_name="products"
    )

    category = models.ForeignKey(Category,on_delete=models.CASCADE)

    title = models.CharField(max_length=200)
    description = models.TextField()

    condition = models.CharField(max_length=20,choices=Condition.choices)

    price = models.DecimalField(max_digits=12, decimal_places=2)
    price_type = models.CharField(max_length=20, choices=PriceType.choices)
    
    region = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    view_count = models.PositiveIntegerField(default=0)
    favorite_count = models.PositiveIntegerField(default=0)
    status = models.CharField( max_length=20,choices=Status.choices,default=Status.MODERATION)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField()

    def __str__(self):
        return self.title
    
class ProductImage(models.Model):

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="products/")
    is_main = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Rasm uchun {self.product.title}"