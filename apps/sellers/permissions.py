from rest_framework.permissions import BasePermission


class IsSeller(BasePermission):
    """
    Faqat role='seller' bo'lgan userlarga ruxsat beradi
    """

    message = "Siz sotuvchi emassiz."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == "seller"
        )
    
class IsSellerOwner(BasePermission):
    """
    Faqat o'zining seller profilini boshqarish huquqi
    """

    message = "Bu profil sizga tegishli emas."

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user