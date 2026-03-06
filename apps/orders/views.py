from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from django.shortcuts import get_object_or_404

from apps.products.models import Product
from .models import Order
from .serializers import OrderCreateSerializer

class OrderCreateView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        product_id = request.data.get("product")
        product = get_object_or_404(Product, id=product_id)
        order = Order.objects.create(
            product=product,
            buyer=request.user,
            seller=product.seller,
            final_price=product.price
        )

        serializer = OrderCreateSerializer(order)

        return Response(serializer.data, status=201)
    
class OrderListView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        role = request.query_params.get("role", "buyer")

        if role == "seller":
            orders = Order.objects.filter(
                seller=request.user
            )

        else:

            orders = Order.objects.filter(
                buyer=request.user
            )
        serializer = OrderCreateSerializer(orders, many=True)

        return Response(serializer.data)
    
class OrderDetailView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, pk):

        order = get_object_or_404(Order, pk=pk)
        if request.user not in [order.buyer, order.seller]:

            return Response(
                {"detail": "Permission denied"},
                status=403
            )

        serializer = OrderCreateSerializer(order)

        return Response(serializer.data)
    
    
class OrderUpdateStatusView(APIView):

    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):

        order = get_object_or_404(Order, pk=pk)

        new_status = request.data.get("status")

        if request.user == order.seller:

            if order.status == Order.Status.PENDING:

                if new_status in ["AGREED", "CANCELED"]:
                    order.status = new_status


        elif request.user == order.buyer:

            if order.status == Order.Status.AGREED:

                if new_status in ["COMPLETED", "CANCELED"]:
                    order.status = new_status

        else:

            return Response(
                {"detail": "Permission denied"},
                status=403
            )

        order.save(update_fields=["status"])

        return Response({"status": order.status})