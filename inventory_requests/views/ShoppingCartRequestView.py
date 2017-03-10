from rest_framework import generics
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from inventory_requests.models import Disbursement
from inventory_requests.serializers.DisbursementSerializer import DisbursementSerializer
from inventory_requests.models import RequestCart
from rest_framework.exceptions import MethodNotAllowed, NotFound, ParseError


class ShoppingCartRequestList(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DisbursementSerializer
    queryset = Disbursement.objects.all()


def get_request(pk):
    try:
        return Disbursement.objects.get(pk=pk)
    except Disbursement.DoesNotExist:
        raise NotFound(detail="Shopping Cart Request not found")


class DeleteShoppingCartRequest(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk, format=None):
        shopping_cart_request = get_request(pk)
        user = self.request.user

        if RequestCart.objects.filter(owner=user, status='active').exists():
            active_shopping_cart = RequestCart.objects.filter(owner=user).get(status='active')
            requests = active_shopping_cart.requests
            #if request exists in active shopping cart
            if requests.filter(id=shopping_cart_request.id).exists():
                shopping_cart_request.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(status=status.HTTP_404_NOT_FOUND)
        else:
            raise MethodNotAllowed("Cannot delete item from shopping cart that is not active")




class ModifyQuantityRequested(generics.UpdateAPIView):
    queryset = RequestTable.objects.all()
    serializer_class = ShoppingCartRequestSerializer
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        quantity = request.data.get('quantity')
        if quantity is None:
            raise MethodNotAllowed(self.patch, detail='Require quantity')
        return self.partial_update(request, *args, **kwargs)

    def perform_update(self, serializer):
        self.get_object()
        request_obj = self.get_object()
        shopping_cart = request_obj.shopping_cart
        if shopping_cart.status != 'active':
            raise MethodNotAllowed(self.patch, "Item with quantity to modify must be part of active cart")
        if serializer.validated_data.get('quantity') <= 0:
            raise ParseError(detail="Quantity must be greater than 0")
        serializer.save()
