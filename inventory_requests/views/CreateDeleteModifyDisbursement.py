from rest_framework import generics
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from inventory_requests.models import Disbursement
from inventory_requests.models import RequestCart
from rest_framework.exceptions import MethodNotAllowed, NotFound, ParseError

from inventory_requests.serializers.DisbursementSerializer import DisbursementSerializer


class CreateDisbursement(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DisbursementSerializer
    queryset = Disbursement.objects.all()


def get_disbursement(pk):
    try:
        return Disbursement.objects.get(pk=pk)
    except Disbursement.DoesNotExist:
        # TODO think about changing the message below
        raise NotFound(detail="Disbursement Request not found")


class DeleteDisbursement(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk, format=None):
        disbursement = get_disbursement(pk)
        user = self.request.user

        if RequestCart.objects.filter(owner=user, status='active').exists():
            active_request_cart = RequestCart.objects.filter(owner=user).get(status='active')
            disbursements = active_request_cart.cart_disbursements
            # if request exists in active request cart
            if disbursements.filter(id=disbursement.id).exists():
                disbursement.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(status=status.HTTP_404_NOT_FOUND)
        else:
            raise MethodNotAllowed("Cannot delete item from request cart that is not active")


class ModifyQuantityRequested(generics.UpdateAPIView):
    queryset = Disbursement.objects.all()
    serializer_class = DisbursementSerializer
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        quantity = request.data.get('quantity')
        if quantity is None:
            raise MethodNotAllowed(self.patch, detail='Quantity required')
        return self.partial_update(request, *args, **kwargs)

    def perform_update(self, serializer):
        self.get_object()
        disbursement = self.get_object()
        request_cart = disbursement.cart
        if request_cart.status != 'active':
            raise MethodNotAllowed(self.patch, "Item with quantity to modify must be part of active cart")
        if serializer.validated_data.get('quantity') <= 0:
            raise ParseError(detail="Quantity must be greater than 0")
        serializer.save()
