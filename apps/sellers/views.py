# apps/sellers/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from .models import SellerProfile
from .serializers import SellerProfileSerializer

from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny

from apps.products.models import Product
from apps.products.serializers import ProductSerializer



class SellerDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, seller_id):
        seller = SellerProfile.objects.filter(id=seller_id).first()
        if not seller:
            return Response({"detail": "Seller not found"}, status=404)

        serializer = SellerProfileSerializer(seller)
        return Response(serializer.data)
    
    
class SellerProductsView(ListAPIView):

    permission_classes = [AllowAny]
    serializer_class = ProductSerializer

    def get_queryset(self):

        seller_id = self.kwargs["seller_id"]

        return Product.objects.select_related("seller","category").filter(seller_id=seller_id, status=Product.Status.ACTIVE)