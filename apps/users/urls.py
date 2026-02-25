from django.urls import path
from .views import telegram_login

urlpatterns = [
    path("auth/telegram-login/", telegram_login, name="telegram_login"),
]