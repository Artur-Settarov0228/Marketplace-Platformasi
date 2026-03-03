from rest_framework import serializers
from .models import SellerProfile

class SellerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = SellerProfile
        fields = ['user', 'shop_name', 'shop_description', 'shop_logo', 'region', 'district']
    