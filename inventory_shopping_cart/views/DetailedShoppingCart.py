from django.http import Http404
from oauth2_provider.ext.rest_framework import TokenHasReadWriteScope

from inventoryProject.permissions import IsAdminOrReadOnly
from inventory_shopping_cart.models import ShoppingCart
from rest_framework.response import Response
from rest_framework.views import APIView

from inventory_shopping_cart.serializers.ShoppingCartSerializer import ShoppingCartSerializer


class ViewDetailedShoppingCart(APIView):
    permission_classes = [TokenHasReadWriteScope, IsAdminOrReadOnly]

    def get_object(self, pk):
        try:
            return ShoppingCart.objects.get(pk=pk)
        except ShoppingCart.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        shopping_cart = self.get_object(pk)
        serializer = ShoppingCartSerializer(shopping_cart)
        return Response(serializer.data)

class ActiveShoppingCart(APIView):
    permission_classes = [TokenHasReadWriteScope, IsAdminOrReadOnly]

    def get_active(self):
        try:
            user = self.request.user
            return ShoppingCart.objects.filter(owner=user).get(status='active')
        except ShoppingCart.DoesNotExist:
            #TODO: fix the reason thing below, instead of using a blank string
            ShoppingCart.objects.create(owner=user, status='active', reason='')
            raise Http404

    def get(self, request, pk, format=None):
        shopping_cart = self.get_object(pk)
        serializer = ShoppingCartSerializer(shopping_cart)
        return Response(serializer.data)