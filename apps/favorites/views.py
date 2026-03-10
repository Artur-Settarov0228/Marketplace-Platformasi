from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from django.shortcuts import get_object_or_404

from apps.favorites.models import Favorite
from apps.favorites.serializers import FavoriteSerializer
from apps.products.models import Product


class FavoriteListView(APIView):
    """
    Foydalanuvchining sevimli mahsulotlari (favorites) bilan ishlash API.

    Endpoint imkoniyatlari:
        GET    -> foydalanuvchining barcha sevimli mahsulotlarini olish
        POST   -> mahsulotni sevimlilarga qo'shish
        DELETE -> mahsulotni sevimlilardan olib tashlash

    Faqat login bo‘lgan foydalanuvchilar foydalanishi mumkin.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request) -> Response:
        """
        Foydalanuvchining barcha sevimli mahsulotlarini qaytaradi.
        """

        favorites = Favorite.objects.select_related(
            "product"
        ).filter(
            user=request.user
        )

        serializer = FavoriteSerializer(favorites, many=True)

        return Response(serializer.data)


    def post(self, request) -> Response:
        """
        Mahsulotni sevimlilar ro'yxatiga qo'shadi.

        Agar mahsulot birinchi marta qo'shilsa:
            product.favorite_count +1 qilinadi
        """

        product_id = request.data.get("product")

        # mahsulot mavjudligini tekshirish
        product = get_object_or_404(Product, id=product_id)

        # favorite yaratish yoki mavjudini olish
        favorite, created = Favorite.objects.get_or_create(
            user=request.user,
            product=product
        )

        # agar yangi favorite yaratilgan bo'lsa count oshiriladi
        if created:
            product.favorite_count += 1
            product.save(update_fields=["favorite_count"])

        return Response(
            {"status": "Mahsulot sevimlilarga qo'shildi"},
            status=status.HTTP_201_CREATED
        )


    def delete(self, request, pk) -> Response:
        """
        Mahsulotni sevimlilar ro'yxatidan o'chiradi.

        Faqat favorite egasi o'chira oladi.
        """

        favorite = get_object_or_404(Favorite, pk=pk)

        # foydalanuvchi favorite egasi emasligini tekshirish
        if favorite.user != request.user:
            return Response(
                {"detail": "Ruxsat berilmadi"},
                status=403
            )

        product = favorite.product

        # favorite o'chirish
        favorite.delete()

        # mahsulot favorite_count ni kamaytirish
        product.favorite_count = max(product.favorite_count - 1, 0)
        product.save(update_fields=["favorite_count"])

        return Response({
            "status": "Mahsulot sevimlilardan o'chirildi"
        })