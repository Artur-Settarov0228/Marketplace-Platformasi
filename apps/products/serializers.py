from rest_framework import serializers
from apps.products.models import Product, ProductImage
from django.utils import timezone
from datetime import timedelta


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
        

class ProductCreateSerializer(serializers.ModelSerializer):

    images = ProductImageSerializer(
        many=True,
        write_only=True,
        required=False
    )

    class Meta:
        model = Product
        fields = [
            "id",
            "title",
            "description",
            "price",
            "category",
            "images"
        ]



    def create(self, validated_data):
        images_data = validated_data.pop("images", [])

        product = Product.objects.create(
            expires_at=timezone.now() + timedelta(days=30),
            **validated_data
        )

        for image_data in images_data:
            ProductImage.objects.create(
                product=product,
                **image_data
            )

        return product
    
class ProductUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = [
            "title",
            "description",
            "price",
            "category",
            "condition",
            "price_type",
            "region",
            "district",
            "expires_at",
        ]