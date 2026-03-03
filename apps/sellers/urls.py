from django.urls import path
from .views import SellerProfileView

urlpatterns = [
    path("sellers/<int:pk>/", SellerProfileView.as_view(), name="seller-profile"),
]