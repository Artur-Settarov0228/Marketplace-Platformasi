from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from django.shortcuts import get_object_or_404

from apps.orders.models import Order
from apps.reviews.models import Review
from apps.reviews.serializers import ReviewSerializer


class ReviewListView(APIView):
    """
    Sotuvchilar uchun yozilgan sharhlar (reviews) ro'yxatini olish API.

    Ushbu endpoint orqali:
        - barcha sharhlarni olish mumkin
        - yoki ma'lum bir sotuvchiga tegishli sharhlarni filtrlash mumkin

    Endpoint:
        GET /api/v1/reviews/?seller_id={seller_id}

    Query params:
        seller_id (optional) -> agar berilsa, faqat shu sotuvchiga tegishli
        sharhlar qaytariladi.
    """

    def get(self, request):
        """
        Review lar ro'yxatini qaytaradi.

        Agar seller_id query parametri berilgan bo'lsa,
        faqat shu sotuvchiga tegishli review lar olinadi.
        """

        seller_id = request.query_params.get("seller_id")

        # Barcha review larni olish
        reviews = Review.objects.all()

        # Agar seller_id berilgan bo'lsa filtr qo'llanadi
        if seller_id:
            reviews = reviews.filter(seller_id=seller_id)

        # Serializer orqali response formatlash
        serializer = ReviewSerializer(reviews, many=True)

        return Response(serializer.data)
    

class ReviewCreateView(APIView):
    """
    Buyurtma asosida sotuvchiga sharh (review) qoldirish API.

    Faqat login bo'lgan foydalanuvchilar sharh qoldira oladi.

    Endpoint:
        POST /api/v1/reviews/

    Request body:
        {
            "order_id": int,
            "rating": int,
            "comment": "text"
        }
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Yangi review yaratadi.

        Jarayon:
        1️⃣ order_id orqali buyurtma topiladi
        2️⃣ buyurtmadagi seller aniqlanadi
        3️⃣ foydalanuvchi reviewer sifatida saqlanadi
        4️⃣ rating va comment bilan review yaratiladi
        """

        order_id = request.data.get("order_id")
        rating = request.data.get("rating")
        comment = request.data.get("comment")

        # Order mavjudligini tekshirish
        order = get_object_or_404(Order, id=order_id)

        # Review yaratish
        review = Review.objects.create(
            order=order,
            reviewer=request.user,
            seller=order.seller,
            rating=rating,
            comment=comment
        )

        # Response serializer
        serializer = ReviewSerializer(review)

        return Response(serializer.data, status=201)