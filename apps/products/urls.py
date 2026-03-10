from django.urls import path
from .views import ProductListView, ProductDetailView, ProductCreateView, ProductUpdateView, ProductDeleteView, ProductPublishView, ProductArchiveView, ProductSoldView


urlpatterns = [
    path("products/", ProductListView.as_view(), name="product-list"),
    path("products/create/", ProductCreateView.as_view(), name="product-create"),

    path("products/<int:pk>/", ProductDetailView.as_view(), name="product-detail"),
    path("products/<int:pk>/update/", ProductUpdateView.as_view(), name="product-update"),
    path("products/<int:pk>/delete/", ProductDeleteView.as_view(), name="product-delete"),

    path("products/<int:pk>/publish/", ProductPublishView.as_view(), name="product-publish"),
    path("products/<int:pk>/archive/", ProductArchiveView.as_view(), name="product-archive"),
    path("products/<int:pk>/sold/", ProductSoldView.as_view(), name="product-sold"),
]