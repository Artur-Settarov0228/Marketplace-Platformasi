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
                status=400
            )

        exists = User.objects.filter(
            telegram_id=telegram_id
        ).exists()

        return Response({"status": exists})

def post(self, request):
    serializer = UserSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user, created = User.objects.get_or_create(
        telegram_id=serializer.validated_data["telegram_id"],
        defaults=serializer.validated_data
    )

    return Response(
        {
            "status": True,
            "created": created
        },
        status=201
    )

class TelegramLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        user_id = request.data.get("chat_id")
        r_code = request.data.get("r_code")

        if not user_id or not r_code:
            return Response({"error": "Missing fields"}, status=400)

        if len(r_code) != 6 or not r_code.isdigit():
            return Response({"error": "Invalid code format"}, status=400)

        stored_code = r.get(f"login_code:{user_id}")

        if not stored_code:
            return Response(
                {"error": "Kod muddati o‘tgan"},
                status=400
            )

        if stored_code != r_code:
            return Response(
                {"error": "Kod noto‘g‘ri"},
                status=400
            )

        try:
            user=User.objects.get(telegram_id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        r.delete(f"login_code:{user_id}")

        refresh = RefreshToken.for_user(user)

        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }, status=200)


class LogoutView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"detail": "Logged out"}, status=200)
        except Exception:
            return Response({"error": "Invalid token"}, status=400)



class UserProfileView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = UserSerializer


    def get(self, request:Request)->Response:
        return Response(UserSerializer(request.user).data)
    
    def patch(self, request:Request)->Response:
        user = request.user

        serializers = UserUpdateSerializer(data = request.data,partial = True)

        if serializers.is_valid(raise_exception=True):
            update_user = serializers.update(user,request.data)

            return Response(UserSerializer(update_user).data)
       