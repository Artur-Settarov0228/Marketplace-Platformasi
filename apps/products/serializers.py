from rest_framework import serializers
from apps.products.models import Product, ProductImage

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"
        read_only_fields = [
            "seller",
            "view_count",
            "favorite_count",
            "status",
            "created_at",
            "updated_at",
            "published_at"
        ]

class ProductImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductImage
        fields = ["id", "image", "is_main"]