from rest_framework import status
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics

from inventoryProject.permissions import IsStaffUser
from inventoryProject.utility.queryset_functions import get_or_not_found
from inventory_requests.models import Loan, Backfill
from inventory_requests.serializers.BackfillSerializer import BackfillSerializer, LoanToBackfillSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import filters


class BackfillList(generics.ListAPIView):
    permission_classes = [IsStaffUser]
    serializer_class = BackfillSerializer
    queryset = Backfill.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('status',)


class ApproveBackfillRequest(APIView):

    def patch(self, request, pk, format=None):
        backfill_request_to_approve = get_or_not_found(Backfill, pk=pk)
        if backfill_request_to_approve.status != 'backfill_request_loan' and backfill_request_to_approve.status != 'backfill_request_outright':
            raise MethodNotAllowed(self.patch, detail="Cannot approve backfill because it is not an active backfill request")
        backfill_request_to_approve.status = 'backfill_transit'
        backfill_request_to_approve.save()
        return Response(BackfillSerializer(backfill_request_to_approve).data, status=status.HTTP_200_OK)



class ConvertLoanToBackfill(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        serializer = LoanToBackfillSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        #TODO should i be using serializer.validated_data here or request.data?
        loan_to_convert = get_or_not_found(Loan, pk=serializer.validated_data.get('pk'))
        request_quantity = serializer.validated_data.get('quantity')
        if loan_to_convert.cart.status != 'fulfilled':
            raise MethodNotAllowed(method=self.post,
                                   detail="Cannot convert a loan to backfill for a loan that is currently not fulfilled")
        if request_quantity > loan_to_convert.quantity:
            raise MethodNotAllowed(method=self.post,
                                   detail="Cannot convert a quantity greater than the current amount loaned out")
        if Backfill.objects.filter(loan=loan_to_convert).exists():
            raise MethodNotAllowed(method=self.post, detail="Backfill already requested for this loan")
        #TODO add call to insert pdf url
        backfill_obj = Backfill.objects.create(loan=loan_to_convert, status='backfill_request_loan',
                                quantity=request_quantity)
        return Response(BackfillSerializer(backfill_obj).data, status=status.HTTP_200_OK)



