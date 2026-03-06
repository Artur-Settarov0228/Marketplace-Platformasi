# apps/favorites/urls.py

from django.urls import path
from .views import FavoriteListView

urlpatterns = [
    path( "favorites/",FavoriteListView.as_view(),name="favorites-list"),
    path("favorites/<int:pk>/",FavoriteListView.as_view(),name="favorites-delete"),

]