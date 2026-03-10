from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny
from rest_framework.generics import RetrieveAPIView

from .models import Category
from .serializers import CategorySerializer
from apps.products.models import Product
from apps.products.serializers import ProductSerializer


class CategoryListView(ListAPIView):
    """
    Asosiy kategoriyalar ro'yxatini olish API.

    Faqat:
        parent = None bo'lgan kategoriyalar chiqariladi
        (ya'ni root kategoriyalar).

    Endpoint:
        GET /api/v1/categories/
    """

    permission_classes = [AllowAny]
    serializer_class = CategorySerializer

    # faqat aktiv va asosiy kategoriyalar
    queryset = Category.objects.filter(
        parent=None,
        is_active=True
    )


class CategoryDetailView(RetrieveAPIView):
    """
    Muayyan kategoriya haqida batafsil ma'lumot olish API.

    Kategoriya slug orqali topiladi.

    Endpoint:
        GET /api/v1/categories/{slug}/
    """

    permission_classes = [AllowAny]
    serializer_class = CategorySerializer

    # slug orqali qidirish
    lookup_field = "slug"

    queryset = Category.objects.filter(
        is_active=True
    )


class CategoryProductsView(ListAPIView):
    """
    Muayyan kategoriya ichidagi mahsulotlar ro'yxatini olish API.

    Faqat:
        status = ACTIVE bo'lgan mahsulotlar chiqariladi.

    Endpoint:
        GET /api/v1/categories/{slug}/products/
    """

    permission_classes = [AllowAny]
    serializer_class = ProductSerializer

    def get_queryset(self):
        """
        Berilgan kategoriya slug bo'yicha mahsulotlarni qaytaradi.
        """

        slug = self.kwargs["slug"]

        return Product.objects.select_related(
            "seller",
            "category"
        ).filter(
            category__slug=slug,
            status=Product.Status.ACTIVE
        )