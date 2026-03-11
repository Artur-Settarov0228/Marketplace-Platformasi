from rest_framework.generics import ListAPIView
from rest_framework.generics import RetrieveAPIView, CreateAPIView, UpdateAPIView, DestroyAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from apps.users.permissions import IsSellerPermission

from django.utils import timezone

from apps.products.filters import ProductFilter
from apps.products.models import Product
from apps.products.serializers import (
    ProductSerializer,
    ProductCreateSerializer,
    ProductUpdateSerializer
)
from apps.products.permissions import IsSeller


class ProductListView(ListAPIView):
    """
    Marketplace dagi barcha aktiv mahsulotlar ro'yxatini olish API.

    Ushbu endpoint orqali:
        - mahsulotlarni ko‘rish
        - filter qilish
        - search qilish
        - ordering qilish mumkin.

    Endpoint:
        GET /api/v1/products/
    """

    permission_classes = [AllowAny]
    serializer_class = ProductSerializer

    queryset = Product.objects.select_related(
        "seller",
        "category"
    ).filter(
        status=Product.Status.ACTIVE
    )

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter
    ]

    filterset_class = ProductFilter
    search_fields = ["title", "description"]

    ordering_fields = [
        "created_at",
        "price",
        "view_count"
    ]

    ordering = ["-created_at"]


class ProductDetailView(RetrieveAPIView):
    """
    Muayyan mahsulot haqida batafsil ma'lumot olish API.

    Mahsulot ochilganda view_count avtomatik oshiriladi.

    Endpoint:
        GET /api/v1/products/{id}/
    """

    permission_classes = [AllowAny]
    serializer_class = ProductSerializer

    queryset = Product.objects.select_related(
        "seller",
        "category"
    )

    def retrieve(self, request, *args, **kwargs):
        """
        Mahsulotni qaytarishdan oldin view_count ni oshiradi.
        """

        product = self.get_object()

        # mahsulot ko'rilganlar sonini oshirish
        product.view_count += 1
        product.save(update_fields=["view_count"])

        serializer = self.get_serializer(product)

        return Response(serializer.data)


class ProductCreateView(CreateAPIView):
    """
    Yangi mahsulot yaratish API.

    Faqat seller bo'lgan foydalanuvchilar mahsulot qo‘sha oladi.

    Mahsulot yaratilganda avtomatik:
        status = MODERATION
    """

    permission_classes = [IsAuthenticated, IsSellerPermission]
    serializer_class = ProductCreateSerializer
    queryset = Product.objects.all()

    def perform_create(self, serializer):
        """
        Mahsulotni seller bilan birga saqlaydi.
        """

        serializer.save(
            seller=self.request.user,
            status=Product.Status.MODERATION
        )


class ProductUpdateView(UpdateAPIView):
    """
    Mahsulot ma'lumotlarini yangilash API.

    Faqat mahsulot egasi (seller) mahsulotni yangilashi mumkin.
    """

    queryset = Product.objects.all()
    serializer_class = ProductUpdateSerializer
    permission_classes = [IsAuthenticated, IsSellerPermission]


class ProductDeleteView(DestroyAPIView):
    """
    Mahsulotni o‘chirish API.

    Aslida mahsulot bazadan o‘chirilmaydi.
    Faqat status = ARCHIVED qilib qo‘yiladi.
    """

    queryset = Product.objects.all()
    permission_classes = [IsAuthenticated, IsSellerPermission]

    def perform_destroy(self, instance):
        """
        Mahsulotni soft delete qilish.
        """

        instance.status = Product.Status.ARCHIVED
        instance.save(update_fields=["status"])


class ProductPublishView(APIView):
    """
    Mahsulotni aktiv qilish (publish) API.

    Seller mahsulotni moderatsiyadan keyin
    aktiv holatga o‘tkazishi mumkin.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        """
        Mahsulot statusini ACTIVE ga o‘zgartiradi.
        """

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
    """
    Mahsulotni arxivga o'tkazish API.

    Bu mahsulotni marketplace dan yashiradi.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        """
        Mahsulot statusini ARCHIVED ga o'zgartiradi.
        """

        product = Product.objects.get(pk=pk)

        if product.seller != request.user:
            return Response({"detail": "Ruxsat berilmadi"}, status=403)

        product.status = Product.Status.ARCHIVED
        product.save(update_fields=["status"])

        return Response({"status": "archived"})


class ProductSoldView(APIView):
    """
    Mahsulot sotilgan deb belgilash API.

    Seller mahsulot sotilgandan keyin
    status = SOLD qilib belgilashi mumkin.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        """
        Mahsulot statusini SOLD ga o'zgartiradi.
        """

        product = Product.objects.get(pk=pk)

        if product.seller != request.user:
            return Response({"detail": "Ruxsat berilmadi"}, status=403)

        product.status = Product.Status.SOLD
        product.save(update_fields=["status"])

        return Response({"status": "Mahsulot sotildi"})