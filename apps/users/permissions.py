from rest_framework.permissions import BasePermission


class IsUserPermission(BasePermission):
    """
    Faqat oddiy foydalanuvchilar (user) uchun ruxsat.

    Agar request yuborgan foydalanuvchi user rolida bo'lmasa
    ushbu endpointga kirish taqiqlanadi.
    """

    message = "Siz oddiy foydalanuvchi emassiz."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.is_user
        )


class IsSellerPermission(BasePermission):
    """
    Faqat sotuvchilar (seller) uchun ruxsat.

    Agar foydalanuvchi seller bo'lmasa
    endpointga kirish taqiqlanadi.
    """

    message = "Siz sotuvchi emassiz!"

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.is_seller
        )