from django.urls import path
from .views import ReviewListView, ReviewCreateView

urlpatterns = [

    path("reviews/", ReviewListView.as_view()),
    path("reviews/", ReviewCreateView.as_view()),

]