from rest_framework import status
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from datetime import datetime

from inventoryProject.permissions import IsStaffUser
from inventoryProject.utility.queryset_functions import get_or_not_found
from inventory_requests.models import Loan, Backfill, Disbursement
from inventory_requests.serializers.BackfillSerializer import BackfillSerializer, CreateBackfillSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import filters

from items.logic.asset_logic import create_asset_helper


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
        associated_loan = get_or_not_found(Loan, pk=serializer.validated_data.get('pk'))
        backfill_request_quantity = serializer.validated_data.get('quantity')
        cart_status = associated_loan.cart.status
        #can request backfill if cart is active, outstanding, fulfilled, or approved
        if cart_status == 'denied' or cart_status == 'cancelled':
            detail_str = "Cannot create backfill request for the current cart because it is {cart_status}".format
            raise MethodNotAllowed(self.post, detail=detail_str(cart_status=cart_status))
        if backfill_request_quantity > associated_loan.quantity:
            raise MethodNotAllowed(method=self.post,
                                   detail="Cannot backfill a quantity greater than the current amount for loan")
        if cart_status == 'fulfilled' and associated_loan.returned_timestamp is not None:
            raise MethodNotAllowed(self.post, "Cannot request backfill because the loan has been fully returned")
        backfill_obj = Backfill.objects.create(loan=associated_loan, status='backfill_request',
                                quantity=backfill_request_quantity, timestamp=datetime.now())
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
        if cart.status == 'outstanding':
            raise MethodNotAllowed(self.patch, detail="Please approve the entire request if you would like to approve"
                                                      " this backfill request")
        #get the backfills that are approved or satisified associated with this loan
        #cannot approve this backfill if total quantity of those approved or satisfied is greater than overall loan quantity
        #e.g. request backfill of 4, then another of 4. both would be in backfill_request state, but annot approve both
        # since would be approving total of 8 when only have 7 loaned out
        approved_quantity = 0
        approved_backfill_requests = backfill_request_to_approve.loan.backfill_loan.filter(status='backfill_transit')
        for backfill in approved_backfill_requests:
            approved_quantity = approved_quantity + backfill.quantity
        potential_approved_quantity = approved_quantity + backfill_request_to_approve.quantity
        if potential_approved_quantity > backfill_request_to_approve.loan.quantity:
            raise MethodNotAllowed(self.patch, detail="Cannot approve this backfill because approving this backfill "
                                                      "would lead to approved quantity exceeding loaned quantity")
        backfill_request_to_approve.status = 'backfill_transit'
        backfill_request_to_approve.timestamp = datetime.now()
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
        if cart.status == 'outstanding':
            raise MethodNotAllowed(self.patch, detail="Please deny the entire request if you would like to deny"
                                                      " this backfill request")
        backfill_request_to_deny.status='backfill_denied'
        backfill_request_to_deny.timestamp = datetime.now()
        backfill_request_to_deny.save()
        return Response(BackfillSerializer(backfill_request_to_deny).data, status=status.HTTP_200_OK)


class FailBackfill(APIView):
    permission_classes = [IsStaffUser]

    def patch(self, request, pk, format=None):
        backfill_request_to_fail = get_or_not_found(Backfill, pk=pk)
        if backfill_request_to_fail.status != 'backfill_transit':
            raise MethodNotAllowed(self.patch, detail="Cannot mark a backfill as failed if it hasn't been approved "
                                                      "first and is not in transit")
        backfill_request_to_fail.status = 'backfill_failed'
        backfill_request_to_fail.timestamp = datetime.now()
        backfill_request_to_fail.save()
        return Response(BackfillSerializer(backfill_request_to_fail).data, status=status.HTTP_200_OK)

#reduce quantity that is loaned out - convert to disbursement, add to available quantity
class SatisfyBackfill(APIView):
    permission_classes = [IsStaffUser]

    def patch(self, request, pk, format=None):
        backfill_request_to_satisfy = get_or_not_found(Backfill, pk=pk)
        if backfill_request_to_satisfy.status != 'backfill_transit':
            raise MethodNotAllowed(self.patch, detail="Cannot mark a backfill as satisfied if it hasn't been approved "
                                                      "first and is not in transit")
        #if backfill request quantity = loaned quantity, then have to get rid of loan and add it as a disbursement
        associated_loan = backfill_request_to_satisfy.loan
        associated_cart = associated_loan.cart
        associated_item = associated_loan.item
        backfill_request_to_satisfy.status = 'backfill_satisfied'
        backfill_request_to_satisfy.save()
        if backfill_request_to_satisfy.quantity == backfill_request_to_satisfy.loan.quantity:
            associated_loan.delete()
        else:
            associated_loan.quantity = associated_loan.quantity - backfill_request_to_satisfy.quantity
            associated_loan.save()
        if associated_cart.cart_disbursements.filter(item=associated_loan.item).exists():
            existing_disbursement = associated_cart.cart_disbursements.get(item=associated_loan.item)
            existing_disbursement.quantity = existing_disbursement.quantity + backfill_request_to_satisfy.quantity
            existing_disbursement.from_backfill = True
            existing_disbursement.save()
        else:
            Disbursement.objects.create(cart=backfill_request_to_satisfy.loan.cart, item=associated_item,
                                        quantity=backfill_request_to_satisfy.quantity, from_backfill=True)
            #add quantity back to available quantity
        associated_item.quantity = associated_item.quantity + backfill_request_to_satisfy.quantity
        associated_item.save()
        if associated_item.is_asset:
            [create_asset_helper(item=associated_item) for x in range(backfill_request_to_satisfy.quantity)]
        # forgive associate loan if any
        #TODO do i need to do this check - will cart status always be fulfilled?
        return Response(BackfillSerializer(backfill_request_to_satisfy).data, status=status.HTTP_200_OK)
