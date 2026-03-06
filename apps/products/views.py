from rest_framework.generics import ListAPIView
from rest_framework.generics import RetrieveAPIView, CreateAPIView, UpdateAPIView, DestroyAPIView, APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from django.utils import timezone

from apps.products.filters import ProductFilter
from apps.products.models import Product
from apps.products.serializers import ProductSerializer, ProductCreateSerializer, ProductUpdateSerializer
from apps.products.permissions import IsProductOwner

class ProductListView(ListAPIView):

    permission_classes = [AllowAny]
    serializer_class = ProductSerializer
    queryset = Product.objects.select_related("seller","category").filter(status=Product.Status.ACTIVE)
    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter
    ]

    filterset_class = ProductFilter
    search_fields = ["title","description"]
    ordering_fields = [
        "created_at",
        "price",
        "view_count"
    ]
    ordering = ["-created_at"]


class ProductDetailView(RetrieveAPIView):

    permission_classes = [AllowAny]
    serializer_class = ProductSerializer
    queryset = Product.objects.select_related( "seller","category")
    
    def retrieve(self, request, *args, **kwargs):

        product = self.get_object()
        product.view_count += 1
        product.save(update_fields=["view_count"])

        serializer = self.get_serializer(product)

        return Response(serializer.data)

class ProductCreateView(CreateAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = ProductCreateSerializer
    queryset = Product.objects.all()

    def perform_create(self, serializer):

        serializer.save(
            seller=self.request.user,
            status=Product.Status.MODERATION
        )


class ProductUpdateView(UpdateAPIView):

    queryset = Product.objects.all()
    serializer_class = ProductUpdateSerializer
    permission_classes = [IsAuthenticated, IsProductOwner]

class ProductDeleteView(DestroyAPIView):

    queryset = Product.objects.all()
    permission_classes = [ IsAuthenticated, IsProductOwner]
    def perform_destroy(self, instance):
        instance.status = Product.Status.ARCHIVED
        instance.save(update_fields=["status"])

class ProductPublishView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):

        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response(
                {"detail": "Mahsulot topilmadi"},
                status=404
            )

        if product.seller != request.user:
            return Response(
                {"detail": "Ruxsat berilmadi"},
                status=403
            )

        product.status = Product.Status.ACTIVE
        product.published_at = timezone.now()
        product.save(update_fields=["status", "published_at"])

        return Response({
            "status": "published"
        })
class ProductArchiveView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):

        product = Product.objects.get(pk=pk)

        if product.seller != request.user:
            return Response({"detail": "Ruxsat berilmadi"}, status=403)

        product.status = Product.Status.ARCHIVED
        product.save(update_fields=["status"])

        return Response({"status": "archived"})
    

    
class ProductSoldView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):

        product = Product.objects.get(pk=pk)

        if product.seller != request.user:
            return Response({"detail": "Ruxsat berilmadi"}, status=403)

        product.status = Product.Status.SOLD
        product.save(update_fields=["status"])

        return Response({"status": "Mahsulot sotildi"})