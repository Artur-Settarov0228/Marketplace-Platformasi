from django.urls import path

from .views import (CategoryListView, CategoryDetailView,CategoryProductsView)

urlpatterns = [
    path("categories/", CategoryListView.as_view()),
    path("categories/<slug:slug>/",CategoryDetailView.as_view()),
    path("categories/<slug:slug>/products/",CategoryProductsView.as_view()),
]