from django.core.files.base import ContentFile
from django.db import transaction
from rest_framework import serializers
from django.contrib.auth import get_user_model

from apps.sellers.models import SellerProfile

from .services import get_image_by_id

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Foydalanuvchini ro'yxatdan o'tkazish va yaratish uchun serializer.

    Bu serializer Telegram orqali kelgan foydalanuvchini
    bazaga saqlash uchun ishlatiladi.

    Qo'shimcha imkoniyatlar:
    - telegram_id orqali foydalanuvchini topish yoki yaratish
    - avatar uchun telegram file_id qabul qilish
    - rasmni Telegram serveridan yuklab olib ImageField ga saqlash
    """

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
        """
        Telegram ID ni tekshiradi.

        Telegram ID manfiy yoki 0 bo'lishi mumkin emas.
        """

        if value <= 0:
            raise serializers.ValidationError("Invalid telegram_id")
        return value

    @transaction.atomic
    def create(self, validated_data):
        """
        Yangi foydalanuvchi yaratish logikasi.

        Jarayon:
         telegram_id orqali foydalanuvchini topish yoki yaratish
         agar yangi user bo'lsa password o'chiriladi
         agar avatar mavjud bo'lsa Telegram API orqali rasm yuklab olinadi
        rasm user avatar fieldiga saqlanadi
        """

        file_id = validated_data.pop("avatar", None)
        telegram_id = validated_data.pop("telegram_id")

        # Telegram ID orqali userni topish yoki yaratish
        user, created = User.objects.get_or_create(
            telegram_id=telegram_id,
            defaults={
                "username": validated_data.get("username") or str(telegram_id),
                "first_name": validated_data.get("first_name"),
                "last_name": validated_data.get("last_name"),
                "phone_number": validated_data.get("phone_number"),
            }
        )

        # Agar user yangi bo'lsa password o'rnatilmaydi
        if created:
            user.set_unusable_password()
            user.save()

        # Agar avatar yuborilgan bo'lsa Telegramdan yuklab olish
        if file_id:
            image_bytes = get_image_by_id(file_id)

            user.avatar.save(
                f"{telegram_id}.jpg",
                ContentFile(image_bytes),
                save=True
            )

        return user
    

class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Foydalanuvchi profil ma'lumotlarini yangilash uchun serializer.

    Bu serializer orqali foydalanuvchi quyidagi ma'lumotlarini
    yangilashi mumkin:
        - username
        - first_name
        - last_name
        - phone_number
    """

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "phone_number",
        ]
        
    def update(self, instance, validated_data):
        """
        Foydalanuvchi ma'lumotlarini yangilaydi.
        DRF ModelSerializer standart update metodidan foydalanadi.
        """

        return super().update(instance, validated_data)


class UpgradeToSellerSerializer(serializers.ModelSerializer):
    """
    Oddiy foydalanuvchini sotuvchiga aylantirish uchun serializer.

    Bu serializer orqali:
        - SellerProfile yaratiladi
        - foydalanuvchi roli seller ga o'zgartiriladi
    """

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
        """
        Foydalanuvchini sotuvchi qilishdan oldin tekshiruvlar.

        Tekshiruvlar:
        foydalanuvchi allaqachon seller emasligini tekshirish
        foydalanuvchida seller profile mavjud emasligini tekshirish
        """

        user = self.context['request'].user

        if user.role == 'seller':
            raise serializers.ValidationError("User is already a seller.")
        
        if hasattr(user, 'seller_profile'):
            raise serializers.ValidationError("User already has a seller profile.")
        
        return attrs
    
    def create(self, validated_data):
        """
        SellerProfile yaratish va user rolini o'zgartirish.

        Jarayon:
        SellerProfile modelini yaratish
        foydalanuvchi rolini SELLER ga o'zgartirish
        """

        user = self.context['request'].user

        seller_profile = SellerProfile.objects.create(
            user=user,
            **validated_data
        )

        user.role = User.Roles.SELLER
        user.save(update_fields=['role'])

        return seller_profile