from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


from django.shortcuts import get_object_or_404

from apps.orders.models import Order
from apps.reviews.models import Review
from apps.reviews.serializers import ReviewSerializer

class ReviewListView(APIView):

    def get(self, request):

        seller_id = request.query_params.get("seller_id")

        reviews = Review.objects.all()

        if seller_id:
            reviews = reviews.filter(seller_id=seller_id)

        serializer = ReviewSerializer(reviews, many=True)

        return Response(serializer.data)
    
class ReviewCreateView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        order_id = request.data.get("order_id")
        rating = request.data.get("rating")
        comment = request.data.get("comment")

        order = get_object_or_404(Order, id=order_id)

        review = Review.objects.create(
            order=order,
            reviewer=request.user,
            seller=order.seller,
            rating=rating,
            comment=comment
        )

        serializer = ReviewSerializer(review)

        return Response(serializer.data, status=201)