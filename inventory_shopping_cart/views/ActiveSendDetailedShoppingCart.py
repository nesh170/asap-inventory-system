from django.http import Http404
from rest_framework import status
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.response import Response
from rest_framework.views import APIView

from inventoryProject.permissions import IsStaffOrReadOnly
from inventory_shopping_cart.models import ShoppingCart
from inventory_shopping_cart.serializers.ShoppingCartSerializer import ShoppingCartSerializer


def get_shopping_cart(pk):
    try:
        return ShoppingCart.objects.get(pk=pk)
    except ShoppingCart.DoesNotExist:
        raise Http404

class ViewDetailedShoppingCart(APIView):
    permission_classes = [IsStaffOrReadOnly]
    def get(self, request, pk, format=None):
        shopping_cart = get_shopping_cart(pk)
        serializer = ShoppingCartSerializer(shopping_cart)
        return Response(serializer.data)

class ActiveShoppingCart(APIView):
    permission_classes = [IsStaffOrReadOnly]
    def get_active(self):
        try:
            user = self.request.user
            return ShoppingCart.objects.filter(owner=user).get(status='active')
        except ShoppingCart.DoesNotExist:
            new_shopping_cart = ShoppingCart.objects.create(owner=user, status='active', reason='Submitting a request for approval')
            return new_shopping_cart

    def get(self, request, format=None):
        shopping_cart = self.get_active()
        serializer = ShoppingCartSerializer(shopping_cart)
        return Response(serializer.data)
class SendCart(APIView):
    def patch(self, request, pk, format=None):
        shopping_cart = get_shopping_cart(pk)
        if (shopping_cart.status=="active"):
            shopping_cart.status = "outstanding"
            #request.data should only contain reason
            serializer = ShoppingCartSerializer(shopping_cart, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            raise MethodNotAllowed(self.patch, "Cannot send this shopping cart because status is not active")