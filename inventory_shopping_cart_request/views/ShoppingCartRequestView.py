from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from inventory_shopping_cart_request.models import RequestTable
from inventory_shopping_cart_request.serializers.ShoppingCartRequestSerializer import ShoppingCartRequestSerializer
from inventory_shopping_cart.models import ShoppingCart
from rest_framework.exceptions import MethodNotAllowed, NotFound


class ShoppingCartRequestList(generics.ListCreateAPIView):
    serializer_class = ShoppingCartRequestSerializer
    queryset = RequestTable.objects.all()

def get_request(pk):
    try:
        return RequestTable.objects.get(pk=pk)
    except RequestTable.DoesNotExist:
        raise NotFound(detail="Shopping Cart Request not found")
class DeleteShoppingCartRequest(APIView):
    def delete(self, request, pk, format=None):
        shopping_cart_request = get_request(pk)
        user = self.request.user
        if (ShoppingCart.objects.filter(owner=user, status='active').exists()):
            active_shopping_cart = ShoppingCart.objects.filter(owner=user).get(status='active')
            requests = active_shopping_cart.requests
            #if request exists in active shopping cart
            if (requests.filter(id=shopping_cart_request.id).exists()):
                shopping_cart_request.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(status=status.HTTP_404_NOT_FOUND)
        else:
            raise MethodNotAllowed("Cannot delete item from shopping cart that is not active")
class ModifyQuantityRequested(APIView):
    def patch(self, request, pk, format=None):
        shopping_cart_request = get_request(pk)
        shopping_cart = shopping_cart_request.shopping_cart
        serializer = ShoppingCartRequestSerializer(shopping_cart_request, data=request.data)
        if (request.data.get('quantity_requested') >= 0 and shopping_cart.status=='active'):
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            if (request.data.get('quantity_requested') < 0 and shopping_cart.status != 'active'):
                raise MethodNotAllowed(self.patch, "Quantity cannot be negative and item with quantity to modify must be part of active cart")
            elif (shopping_cart.status != 'active'):
                raise MethodNotAllowed(self.patch, "Item with quantity to modify must be part of active cart")
            elif (request.data.get('quantity_requested') < 0):
                raise MethodNotAllowed(self.patch, "Quantity cannot be negative")
            #should never reach this else statement
            else:
                raise MethodNotAllowed(self.patch, "Method not allowed")