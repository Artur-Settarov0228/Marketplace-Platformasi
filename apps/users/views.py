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

    def post(self, request:Request)->Response:
        r_code = request.data.get("r_code")

        if r_code is None or len(r_code) != 6 or not r_code.isdigit():
            return Response({"code":"error"},status=status.HTTP_400_BAD_REQUEST)
        
        user_id = r.get(f"login_code:{r_code}")

        if not user_id:
            return Response(
                {"error": "Kod xato yoki muddati o‘tgan"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(chat_id = user_id)
        except User.DoesNotExist:
            return Response("user not found",status=400)
        
        r.delete(f"login_user:{user_id}")
        r.delete(f"login_code:{r_code}")

        token = RefreshToken.for_user(user)

        return Response({
                "refresh": str(token),
                "access": str(token.access_token),
            },status=200)


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
       