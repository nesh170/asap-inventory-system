import django_filters
from rest_framework import generics
from rest_framework import status
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from inventoryProject.utility.queryset_functions import get_or_not_found
from inventory_requests.models import Disbursement
from inventory_requests.serializers.DisbursementSerializer import DisbursementSerializer


class CreateDisbursement(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DisbursementSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filter_fields = ('cart__status', 'item__name', 'cart__owner__username')

    def get_queryset(self):
        user = self.request.user
        return Disbursement.objects.all() if user.is_staff else Disbursement.objects.filter(cart__owner=user)


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
