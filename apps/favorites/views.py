from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from django.shortcuts import get_object_or_404

from apps.favorites.models import Favorite
from apps.favorites.serializers import FavoriteSerializer
from apps.products.models import Product


class FavoriteListView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request) -> Response:

        favorites = Favorite.objects.select_related(
            "product"
        ).filter(
            user=request.user
        )
        serializer = FavoriteSerializer(favorites, many=True)

        return Response(serializer.data)


    def post(self, request) -> Response:

        product_id = request.data.get("product")
        product = get_object_or_404(Product, id=product_id)
        favorite, created = Favorite.objects.get_or_create(
            user=request.user,
            product=product
        )

        if created:
            product.favorite_count += 1
            product.save(update_fields=["favorite_count"])

        return Response(
            {"status": "qo'shildi"},
            status=status.HTTP_201_CREATED
        )


    def delete(self, request, pk) -> Response:
        favorite = get_object_or_404(Favorite, pk=pk)

        if favorite.user != request.user:
            return Response(
                {"detail": "Ruxsat berilmadi"},status=403)

        product = favorite.product
        favorite.delete()
        product.favorite_count = max(product.favorite_count - 1, 0)
        product.save(update_fields=["favorite_count"])

        return Response({"status": "uchirilib tashlandi ␡"})