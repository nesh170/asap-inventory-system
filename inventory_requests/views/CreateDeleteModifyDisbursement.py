from rest_framework import generics
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from inventoryProject.utility.queryset_functions import get_or_not_found
from inventory_requests.models import Disbursement
from inventory_requests.models import RequestCart
from rest_framework.exceptions import MethodNotAllowed, NotFound, ParseError

from inventory_requests.serializers.DisbursementSerializer import DisbursementSerializer


class CreateDisbursement(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DisbursementSerializer
    queryset = Disbursement.objects.all()


class DeleteDisbursement(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk, format=None):
        disbursement = get_or_not_found(Disbursement, pk=pk)
        user = self.request.user
        if disbursement.cart.status == 'active' and (disbursement.cart.owner == user or
                                                             disbursement.cart.staff == user):
            disbursement.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            raise MethodNotAllowed("Cannot delete disbursement from request cart that is not active")


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
        request_cart = self.get_object().cart
        if request_cart.status != 'active':
            raise MethodNotAllowed(self.patch, "Item with quantity to modify must be part of active cart")
        if serializer.validated_data.get('quantity') <= 0:
            raise ParseError(detail="Quantity must be greater than 0")
        serializer.save()
