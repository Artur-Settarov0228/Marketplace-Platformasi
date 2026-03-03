from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.request import Request
from .models import SellerProfile
from .serializers import SellerProfileSerializer

class SellerProfileView(APIView):
    permission_classes = [AllowAny]

    def get(self, request: Request):
        pk = request.query_params.get("pk")
        seller = SellerProfile.objects.filter(pk=pk).first()

        serializers = SellerProfileSerializer(seller)
        serializers.is_valid(raise_exception=True)

        return Response(serializers.data)



        