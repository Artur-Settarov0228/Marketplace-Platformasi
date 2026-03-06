from django.urls import path
from .views import (
    OrderListView,
    OrderCreateView,
    OrderDetailView,
    OrderUpdateStatusView
)

urlpatterns = [

    path("orders/", OrderListView.as_view()),
    path("orders/", OrderCreateView.as_view()),
    path("orders/<int:pk>/", OrderDetailView.as_view()),
    path("orders/<int:pk>/", OrderUpdateStatusView.as_view()),
]