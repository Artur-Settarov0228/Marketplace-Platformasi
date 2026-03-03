from django.core.files.base import ContentFile
from django.db import transaction
from rest_framework import serializers
from django.contrib.auth import get_user_model

from apps.sellers.models import SellerProfile

from .services import get_image_by_id

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    telegram_id = serializers.IntegerField(write_only=True)
    avatar = serializers.CharField(write_only=True, required=False)
    username = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = User
        fields = [
            "telegram_id",
            "username",
            "first_name",
            "last_name",
            "phone_number",
            "avatar",
        ]

    def validate_telegram_id(self, value):
        if value <= 0:
            raise serializers.ValidationError("Invalid telegram_id")
        return value

    @transaction.atomic
    def create(self, validated_data):
        file_id = validated_data.pop("avatar", None)
        telegram_id = validated_data.pop("telegram_id")

        user, created = User.objects.get_or_create(
            telegram_id=telegram_id,
            defaults={
                "username": validated_data.get("username") or str(telegram_id),
                "first_name": validated_data.get("first_name"),
                "last_name": validated_data.get("last_name"),
                "phone_number": validated_data.get("phone_number"),
            }
        )

        if created:
            user.set_unusable_password()
            user.save()

        if file_id:
            image_bytes = get_image_by_id(file_id)
            user.avatar.save(
                f"{telegram_id}.jpg",
                ContentFile(image_bytes),
                save=True
            )

        return user
    

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "phone_number",
        ]
        
    def update(self, instance, validated_data):
        return super().update(instance, validated_data)


class UpgradeToSellerSerializer(serializers.ModelSerializer):
    class Meta:
        model = SellerProfile
        fields = [
            "shop_name",
            "shop_description",
            "shop_logo",
            "region",
            "district"
        ]
    
    def validate(self, attrs):
        user = self.context['request'].user

        if user.role == 'seller':
            raise serializers.ValidationError("User is already a seller.")
        
        if hasattr(user, 'seller_profile'):
            raise serializers.ValidationError("User already has a seller profile.")
        
        return attrs
    
    def create(self, validated_data):
        user = self.context['request'].user
        seller_profile = SellerProfile.objects.create(user=user, **validated_data)
        user.role = User.Roles.SELLER
        user.save(update_fields=['role'])
        return seller_profile
    