from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from django.shortcuts import get_object_or_404

from apps.products.models import Product
from .models import Order
from .serializers import OrderCreateSerializer


class OrderCreateView(APIView):
    """
    Buyurtma yaratish API.

    Foydalanuvchi mahsulotni tanlab buyurtma beradi.
    Buyurtma yaratilganda:
        - buyer -> request.user
        - seller -> product.seller
        - final_price -> product.price
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Yangi buyurtma yaratadi.
        """

        product_id = request.data.get("product")

        # Mahsulotni bazadan olish
        product = get_object_or_404(Product, id=product_id)

        # Buyurtma yaratish
        order = Order.objects.create(
            product=product,
            buyer=request.user,
            seller=product.seller,
            final_price=product.price
        )

        serializer = OrderCreateSerializer(order)

        return Response(serializer.data, status=201)


class OrderListView(APIView):
    """
    Foydalanuvchining buyurtmalari ro'yxatini olish API.

    Query param:
        role=buyer   -> foydalanuvchi qilgan buyurtmalar
        role=seller  -> foydalanuvchiga kelgan buyurtmalar
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Buyurtmalar ro'yxatini qaytaradi.
        """

        role = request.query_params.get("role", "buyer")

        if role == "seller":

            # Sellerga kelgan buyurtmalar
            orders = Order.objects.filter(
                seller=request.user
            )

        else:

            # Buyer qilgan buyurtmalar
            orders = Order.objects.filter(
                buyer=request.user
            )

        serializer = OrderCreateSerializer(orders, many=True)

        return Response(serializer.data)


class OrderDetailView(APIView):
    """
    Muayyan buyurtma haqida batafsil ma'lumot olish API.

    Buyurtmani faqat:
        - buyer
        - seller
    ko‘ra oladi.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        """
        Buyurtma tafsilotlarini qaytaradi.
        """

        order = get_object_or_404(Order, pk=pk)

        # Agar foydalanuvchi buyer ham seller ham bo'lmasa
        if request.user not in [order.buyer, order.seller]:

            return Response(
                {"detail": "Ruxsat berilmadi"},
                status=403
            )

        serializer = OrderCreateSerializer(order)

        return Response(serializer.data)


class OrderUpdateStatusView(APIView):
    """
    Buyurtma statusini o'zgartirish API.

    Status o'zgarish qoidalari:

    Seller:
        PENDING -> AGREED yoki CANCELED

    Buyer:
        AGREED -> COMPLETED yoki CANCELED
    """

    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        """
        Buyurtma statusini yangilaydi.
        """

        order = get_object_or_404(Order, pk=pk)

        new_status = request.data.get("status")

        # Agar seller status o'zgartirayotgan bo'lsa
        if request.user == order.seller:

            if order.status == Order.Status.PENDING:

                if new_status in ["AGREED", "CANCELED"]:
                    order.status = new_status

        # Agar buyer status o'zgartirayotgan bo'lsa
        elif request.user == order.buyer:

            if order.status == Order.Status.AGREED:

                if new_status in ["COMPLETED", "CANCELED"]:
                    order.status = new_status

        else:

            return Response(
                {"detail": "Ruxsat berilmadi"},
                status=403
            )

        order.save(update_fields=["status"])

        return Response({"status": order.status})