from django.http import Http404
from oauth2_provider.ext.rest_framework import TokenHasReadWriteScope
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from inventory_shopping_cart_request.models import RequestTable
from inventory_shopping_cart_request.serializers.ShoppingCartRequestSerializer import ShoppingCartRequestSerializer
from inventory_shopping_cart.models import ShoppingCart

class ShoppingCartRequestList(generics.ListCreateAPIView):
    permission_classes = [TokenHasReadWriteScope]
    serializer_class = ShoppingCartRequestSerializer
    queryset = RequestTable.objects.all()


class DeleteShoppingCartRequest(APIView):

    permission_classes = [TokenHasReadWriteScope]
    def get_object(self, pk):
        try:
            return RequestTable.objects.get(pk=pk)
        except RequestTable.DoesNotExist:
            raise Http404

    def delete(self, request, pk, format=None):
        shopping_cart_request = self.get_object(pk)
        user = self.request.user
        active_shopping_cart = ShoppingCart.objects.filter(owner=user).get(status='active')
        requests = active_shopping_cart.requests
        #if request exists in active shopping cart
        if (requests.filter(id=shopping_cart_request.id).exists()):
            shopping_cart_request.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

