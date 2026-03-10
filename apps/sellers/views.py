# apps/sellers/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from apps.sellers.models import SellerProfile
from apps.sellers.serializers import SellerProfileSerializer

from rest_framework.generics import ListAPIView

from apps.products.models import Product
from apps.products.serializers import ProductSerializer


class SellerDetailView(APIView):
    """
    Sotuvchi haqida umumiy ma'lumotni olish uchun API.

    Bu endpoint orqali frontend yoki boshqa servislar
    sotuvchining profil ma'lumotlarini korishi mumkin.

    Endpoint:
        GET /api/v1/sellers/{seller_id}/
    """

    permission_classes = [AllowAny]

    def get(self, request, seller_id):
        """
        Berilgan seller_id orqali sotuvchi profilini qaytaradi.

        Parametrlar:
            seller_id (int): sotuvchining ID si

        Response:
            200 -> SellerProfile ma'lumotlari
            404 -> Sotuvchi topilmasa
        """

        # SellerProfile ni bazadan olish
        seller = SellerProfile.objects.filter(id=seller_id).first()

        if not seller:
            return Response(
                {"detail": "Sotuvchi topilmadi"},
                status=404
            )

        # serializer orqali response tayyorlash
        serializer = SellerProfileSerializer(seller)

        return Response(serializer.data)
    
    
class SellerProductsView(ListAPIView):
    """
    Muayyan sotuvchining barcha aktiv mahsulotlarini chiqarish API.

    Bu endpoint marketplace yoki katalog sahifasida
    sotuvchining mahsulotlarini korsatish uchun ishlatiladi.

    Endpoint:
        GET /api/v1/sellers/{seller_id}/products/
    """

    permission_classes = [AllowAny]
    serializer_class = ProductSerializer

    def get_queryset(self):
        """
        Berilgan seller_id boyicha mahsulotlarni qaytaradi.

        Faqat:
            status = ACTIVE bo'lgan mahsulotlar olinadi.

        select_related ishlatilgan:
            - seller
            - category

        Bu N+1 query muammosini oldini oladi va
        query performance ni yaxshilaydi.
        """

        seller_id = self.kwargs["seller_id"]

        return Product.objects.select_related(
            "seller",
            "category"
        ).filter(
            seller_id=seller_id,
            status=Product.Status.ACTIVE
        )