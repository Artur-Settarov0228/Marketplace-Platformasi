from django.contrib.auth import get_user_model
import redis


from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from .serializers import UserSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework import status
from rest_framework_simplejwt.exceptions import TokenError

from apps.users.serializers import UpgradeToSellerSerializer


from django.db import transaction


from .serializers import UserUpdateSerializer


User = get_user_model()

r = redis.Redis(
    host='127.0.0.1',
    port=6379,
    decode_responses=True
)


class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        telegram_id = request.query_params.get("telegram_id")

        if not telegram_id:
            return Response(
                {"error": "telegram_id required"},
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
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "status": True,
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            status=201
        )


class TelegramLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        code = request.data.get("code")

        if not isinstance(code, str) or not code.isdigit() or len(code) != 6:
            return Response(
                {"error": "Invalid code format"},
                status=400
            )

        redis_key = f"login_code:{code}"
        user_id = r.get(redis_key)

        if not user_id:
            return Response(
                {"error": "Kod xato yoki muddati o‘tgan"},
                status=400
            )

        try:
            user = User.objects.get(telegram_id=int(user_id))
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=404
            )

        r.delete(redis_key)
        r.delete(f"login_user:{user_id}")

        refresh = RefreshToken.for_user(user)

        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        })
    


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return Response(
                {"error": "Refresh token required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError:
            return Response(
                {"error": "Invalid or expired token"},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {"message": "Successfully logged out"},
            status=status.HTTP_200_OK
        )

class UserProfileView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request: Request) -> Response:
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
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request:Request):
        serializers = UpgradeToSellerSerializer(data = request.data, context = {"request": request})
        serializers.is_valid(raise_exception=True)
        seller_profile = serializers.save()

        return Response({"message":"Siz endi sotuvchisiz", "shop_name":seller_profile.shop_name})