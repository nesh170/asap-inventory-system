from rest_framework import status
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics

from inventoryProject.permissions import IsStaffUser
from inventoryProject.utility.queryset_functions import get_or_not_found
from inventory_requests.models import Loan, Backfill, Disbursement
from inventory_requests.serializers.BackfillSerializer import BackfillSerializer, CreateBackfillSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import filters


class BackfillList(generics.ListAPIView):
    permission_classes = [IsStaffUser]
    serializer_class = BackfillSerializer
    queryset = Backfill.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('status',)


#TODO add support for PDF
#TODO how are we handling multiple backfill requests for the same item?
class CreateBackfillRequest(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        serializer = CreateBackfillSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        #TODO should i be using serializer.validated_data here or request.data?
        associated_loan = get_or_not_found(Loan, pk=serializer.validated_data.get('pk'))
        backfill_request_quantity = serializer.validated_data.get('quantity')
        cart_status = associated_loan.cart.status
        if cart_status != 'active' and cart_status != 'outstanding' and cart_status != 'fulfilled':
            detail_str = "Cannot create backfill request for the current cart because it is {cart_status}".format
            raise MethodNotAllowed(self.post, detail=detail_str(cart_status=cart_status))
        if backfill_request_quantity > associated_loan.quantity:
            raise MethodNotAllowed(method=self.post,
                                   detail="Cannot backfill a quantity greater than the current amount for loan")
        if cart_status == 'fulfilled' and associated_loan.returned_timestamp is not None:
            raise MethodNotAllowed(self.post, "Cannot request backfill because the loan has been fully returned")
        backfill_obj = Backfill.objects.create(loan=associated_loan, status='backfill_request',
                                quantity=backfill_request_quantity)
        return Response(BackfillSerializer(backfill_obj).data, status=status.HTTP_200_OK)


class ApproveBackfillRequest(APIView):
    permission_classes = [IsStaffUser]

    def patch(self, request, pk, format=None):
        backfill_request_to_approve = get_or_not_found(Backfill, pk=pk)
        if backfill_request_to_approve.status != 'backfill_request':
            raise MethodNotAllowed(self.patch, detail="Cannot approve backfill because it is not an "
                                                      "outstanding backfill request")
        cart = backfill_request_to_approve.loan.cart
        #to prevent them from calling this api for a request that is outstanding
        if cart.status != 'fulfilled':
            raise MethodNotAllowed(self.patch, detail="Please approve the entire request if you would like to approve"
                                                      "this backfill request")
        backfill_request_to_approve.status = 'backfill_transit'
        backfill_request_to_approve.save()
        return Response(BackfillSerializer(backfill_request_to_approve).data, status=status.HTTP_200_OK)


class DenyBackfillRequest(APIView):
    permission_classes = [IsStaffUser]

    def patch(self, request, pk, format=None):
        backfill_request_to_deny = get_or_not_found(Backfill, pk=pk)
        if backfill_request_to_deny.status != 'backfill_request':
            raise MethodNotAllowed(self.patch, detail="Cannot deny backfill because it is not an "
                                                      "outstanding backfill request")
        cart = backfill_request_to_deny.loan.cart
        if cart.status != 'fulfilled':
            raise MethodNotAllowed(self.patch, detail="Please deny the entire request if you would like to deny"
                                                      "this backfill request")
        backfill_request_to_deny.status='backfill_denied'
        backfill_request_to_deny.save()
        return Response(BackfillSerializer(backfill_request_to_deny).data, status=status.HTTP_200_OK)


#TODO finish this view
class FailBackfill(APIView):
    permission_classes = [IsStaffUser]

    def patch(self, request, pk, format=None):
        backfill_request_to_fail = get_or_not_found(Backfill, pk=pk)
        if backfill_request_to_fail.status != 'backfill_transit':
            raise MethodNotAllowed(self.patch, detail="Cannot mark a backfill as failed if it hasn't been approved "
                                                      "first and is not in transit")
        backfill_request_to_fail.status = 'backfill_failed'
        backfill_request_to_fail.save()


class SatisfyBackfill(APIView):
    permission_classes = [IsStaffUser]

    def patch(self, request, pk, format=None):
        backfill_request_to_satisfy = get_or_not_found(Backfill, pk=pk)
        if backfill_request_to_satisfy.status != 'backfill_transit':
            raise MethodNotAllowed(self.patch, detail="Cannot mark a backfill as satisfied if it hasn't been approved "
                                                      "first and is not in transit")
        #add quantity back to available quantity
        item_backfilled = backfill_request_to_satisfy.loan.item
        item_backfilled.quantity = item_backfilled.quantity + backfill_request_to_satisfy.quantity
        item_backfilled.save()
        backfill_request_to_satisfy.status = 'backfill_satisfied'
        backfill_request_to_satisfy.save()
        # forgive associate loan if any
        #TODO do i need to do this check - will cart status always be fulfilled?
        if backfill_request_to_satisfy.loan.cart.status == 'fulfilled':
            Disbursement.objects.create(cart=backfill_request_to_satisfy.loan.cart, item=item_backfilled,
                                        quantity=backfill_request_to_satisfy.quantity, from_backfill=True)
        return Response(BackfillSerializer(backfill_request_to_satisfy).data, status=status.HTTP_200_OK)
