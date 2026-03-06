from rest_framework import serializers
from apps.favorites.models import Favorite
from apps.products.serializers import ProductSerializer


class FavoriteSerializer(serializers.ModelSerializer):

    product = ProductSerializer(read_only = True)

    class Meta:
        model = Favorite
        fields = [
            "id",
            "product",
            "created_at"
        ]

