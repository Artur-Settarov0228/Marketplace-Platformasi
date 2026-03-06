from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny
from rest_framework.generics import RetrieveAPIView


from .models import Category
from .serializers import CategorySerializer
from apps.products.models import Product
from apps.products.serializers import ProductSerializer



class CategoryListView(ListAPIView):

    permission_classes = [AllowAny]
    serializer_class = CategorySerializer
    queryset = Category.objects.filter( parent=None, is_active=True)



class CategoryDetailView(RetrieveAPIView):

    permission_classes = [AllowAny]
    serializer_class = CategorySerializer
    lookup_field = "slug"
    queryset = Category.objects.filter(is_active=True)



class CategoryProductsView(ListAPIView):

    permission_classes = [AllowAny]
    serializer_class = ProductSerializer

    def get_queryset(self):
        slug = self.kwargs["slug"]

        return Product.objects.select_related( "seller","category").filter(category__slug=slug, status=Product.Status.ACTIVE)