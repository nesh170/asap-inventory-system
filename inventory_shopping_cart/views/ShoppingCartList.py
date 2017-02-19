from oauth2_provider.ext.rest_framework import TokenHasReadWriteScope
from rest_framework import generics

from inventory_shopping_cart.models import ShoppingCart
from inventory_shopping_cart.serializers.ShoppingCartSerializer import ShoppingCartSerializer


class ShoppingCartList(generics.ListCreateAPIView):
    permission_classes = [TokenHasReadWriteScope]
    serializer_class = ShoppingCartSerializer
    def get_queryset(self):
        user = self.request.user
        return ShoppingCart.objects.exclude(status="cancelled") if user.is_staff \
            else ShoppingCart.objects.filter(owner=user).exclude(status="cancelled")