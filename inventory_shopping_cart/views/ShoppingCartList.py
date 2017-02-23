from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from inventory_shopping_cart.models import ShoppingCart
from inventory_shopping_cart.serializers.ShoppingCartSerializer import ShoppingCartSerializer


class ShoppingCartList(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ShoppingCartSerializer
    def get_queryset(self):
        user = self.request.user
        #TODO make sure this check is correct (for is_staff)
        return ShoppingCart.objects.exclude(status="cancelled") if user.is_staff \
            else ShoppingCart.objects.filter(owner=user).exclude(status="cancelled")