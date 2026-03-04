from rest_framework import serializers
from .models import SellerProfile

class SellerProfileSerializer(serializers.ModelSerializer):
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    class Meta:
        model = SellerProfile
        fields = ['shop_name', 'shop_description', 'shop_logo', 'region', 'district', 'first_name', 'last_name']

    def get_first_name(self, obj):
        return obj.user.first_name
    
    def get_last_name(self, obj):
        return obj.user.last_name
    