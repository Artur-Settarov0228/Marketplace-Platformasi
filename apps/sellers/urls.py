from django.urls import path
from .views import SellerDetailView, SellerProductsView

urlpatterns = [
    path("sellers/<int:seller_id>/", SellerDetailView.as_view(),name="seller-detail"),
    path("sellers/<int:seller_id>/products/",SellerProductsView.as_view(), name="seller-products"),

]