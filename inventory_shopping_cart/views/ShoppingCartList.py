from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from inventory_shopping_cart.models import ShoppingCart
from inventory_shopping_cart.serializers.ShoppingCartSerializer import ShoppingCartSerializer
from rest_framework import filters


class ShoppingCartList(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ShoppingCartSerializer
    filter_backends = (filters.SearchFilter, filters.DjangoFilterBackend)
    filter_fields = ('status', 'requests__item__name', )
    search_fields = ('owner__username', 'reason', 'requests__item__name', )

    def get_queryset(self):
        user = self.request.user
        return ShoppingCart.objects.exclude(status="cancelled") if user.is_staff \
            else ShoppingCart.objects.filter(owner=user).exclude(status="cancelled")