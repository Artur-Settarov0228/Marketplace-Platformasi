from django.contrib.auth import get_user_model
import redis

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from .serializers import UserSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework import status
from rest_framework_simplejwt.exceptions import TokenError

from apps.users.serializers import UpgradeToSellerSerializer

from django.db import transaction

from .serializers import UserUpdateSerializer

"""
Redis konfiguratsiyasi va foydalanuvchi modeli olish.
Redis login kodlarini saqlash va tekshirish uchun ishlatiladi.
"""
User = get_user_model()

r = redis.Redis(
    host='127.0.0.1',
    port=6379,
    decode_responses=True
)


class RegisterAPIView(APIView):
    """
    Foydalanuvchini ro'yxatdan o'tkazish uchun API.

    GET:
        Telegram ID orqali foydalanuvchi mavjudligini tekshiradi.

    POST:
        Yangi foydalanuvchini yaratadi va unga JWT token beradi.
    """

    permission_classes = [AllowAny]

    def get(self, request):
        """
        Telegram ID mavjud yoki yo'qligini tekshiradi.

        Query params:
            telegram_id

        Response:
            {
                "status": true/false
            }
        """

        telegram_id = request.query_params.get("telegram_id")

        if not telegram_id:
            return Response(
                {"error": "telegram_id kiritilishi shart"},
                status=status.HTTP_400_BAD_REQUEST
            )

        exists = User.objects.filter(
            telegram_id=telegram_id
        ).exists()

        return Response(
            {"status": exists},
            status=status.HTTP_200_OK
        )

    def post(self, request):
        """
        Yangi foydalanuvchini ro'yxatdan o'tkazadi.

        Request body:
            user ma'lumotlari

        Response:
            JWT refresh va access token qaytaradi.
        """

        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "status": True,
                "message": "Foydalanuvchi muvaffaqiyatli ro'yxatdan o'tdi",
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            status=201
        )


class TelegramLoginView(APIView):
    """
    Telegram orqali login qilish API.

    Telegram bot orqali yuborilgan 6 xonali kod
    Redis orqali tekshiriladi va foydalanuvchi tizimga kiradi.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        """
        Login kodini tekshiradi va JWT token beradi.

        Request body:
            code (6 xonali kod)

        Response:
            refresh va access token
        """

        code = request.data.get("code")

        if not isinstance(code, str) or not code.isdigit() or len(code) != 6:
            return Response(
                {"error": "Kod formati noto'g'ri"},
                status=400
            )

        redis_key = f"login_code:{code}"
        user_id = r.get(redis_key)

        if not user_id:
            return Response(
                {"error": "Kod noto'g'ri yoki muddati tugagan"},
                status=400
            )

        try:
            user = User.objects.get(telegram_id=int(user_id))
        except User.DoesNotExist:
            return Response(
                {"error": "Foydalanuvchi topilmadi"},
                status=404
            )

        r.delete(redis_key)
        r.delete(f"login_user:{user_id}")

        refresh = RefreshToken.for_user(user)

        return Response({
            "message": "Tizimga muvaffaqiyatli kirildi",
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        })


class LogoutView(APIView):
    """
    Foydalanuvchini tizimdan chiqarish API.

    Refresh token blacklist qilinadi.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Refresh tokenni blacklist qilib logout qiladi.

        Request body:
            refresh token
        """

        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return Response(
                {"error": "Refresh token yuborilishi kerak"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError:
            return Response(
                {"error": "Token noto'g'ri yoki muddati tugagan"},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {"message": "Tizimdan muvaffaqiyatli chiqildi"},
            status=status.HTTP_200_OK
        )


class UserProfileView(APIView):
    """
    Foydalanuvchi profilini ko'rish va yangilash API.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        """
        Joriy foydalanuvchi profil ma'lumotlarini qaytaradi.
        """

        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request: Request) -> Response:
        """
        Foydalanuvchi profilini qisman yangilaydi.
        """

        user = request.user

        serializer = UserUpdateSerializer(
            instance=user,
            data=request.data,
            partial=True
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(UserSerializer(user).data)


class UpgradeToSellerView(APIView):
    """
    Oddiy foydalanuvchini sotuvchi (seller) ga aylantirish API.
    """

    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request: Request):
        """
        Foydalanuvchini seller sifatida ro'yxatdan o'tkazadi.

        Request body:
            shop_name va boshqa seller ma'lumotlari

        Response:
            sotuvchi bo'lganligi haqida xabar
        """

        serializers = UpgradeToSellerSerializer(
            data=request.data,
            context={"request": request}
        )

        serializers.is_valid(raise_exception=True)
        seller_profile = serializers.save()

        return Response({
            "message": "Siz endi sotuvchisiz",
            "shop_name": seller_profile.shop_name
        })