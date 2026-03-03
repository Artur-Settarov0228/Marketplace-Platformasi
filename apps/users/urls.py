from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import RegisterAPIView, UserProfileView, TelegramLoginView, LogoutView, UpgradeToSellerView


urlpatterns = [
    path("auth/register/", RegisterAPIView.as_view(), name="register"),
    path("auth/telegram-login/", TelegramLoginView.as_view(), name="telegram-login"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="refresh"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
    
    path("me/", UserProfileView.as_view(), name="user-me"),
    path("user/me/upgrade-to-seller/", UpgradeToSellerView.as_view(), name="upgrade-to-seller")


    
    
]