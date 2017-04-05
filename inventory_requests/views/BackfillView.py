from rest_framework import status
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.permissions import IsAuthenticated

from inventoryProject.utility.queryset_functions import get_or_not_found
from inventory_requests.models import Loan, Backfill
from inventory_requests.serializers.BackfillSerializer import BackfillSerializer, LoanToBackfillSerializer
from rest_framework.response import Response
from rest_framework.views import APIView



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
        #TODO add call to insert pdf url
        backfill_obj = Backfill.objects.create(cart=loan_to_convert.cart, item=loan_to_convert.item,
                                quantity=request_quantity)
        loan_to_convert.quantity = loan_to_convert.quantity - request_quantity
        loan_to_convert.save()
        return Response(BackfillSerializer(backfill_obj).data, status=status.HTTP_200_OK)



