from rest_framework import serializers
from .models import Order


class OrderCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = [
            "id",
            "product",
            "final_price",
            "status",
            "created_at"
        ]

        read_only_fields = ["final_price", "status"]