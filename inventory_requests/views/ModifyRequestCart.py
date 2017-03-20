from datetime import datetime

from django.contrib.auth.models import User
from rest_framework import generics
from rest_framework import status
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from inventoryProject.permissions import IsStaffUser
from inventoryProject.utility.queryset_functions import get_or_not_found
from inventory_requests.business_logic import modify_request_cart_logic
from inventory_requests.business_logic.modify_request_cart_logic import start_loan
from inventory_requests.models import RequestCart, Disbursement, Loan
from inventory_requests.serializers.DisbursementSerializer import LoanSerializer, DisbursementSerializer
from inventory_requests.serializers.RequestCartSerializer import RequestCartSerializer, QuantitySerializer
from inventory_requests.serializers.RequestStatusSerializer import ApproveDenySerializer, StaffDisburseSerializer
from inventory_transaction_logger.action_enum import ActionEnum
from inventory_transaction_logger.utility.logger import LoggerUtility

TYPE_MAP = {'loan': Loan, 'disbursement': Disbursement}
SERIALIZER_MAP = {'loan': LoanSerializer, 'disbursement': DisbursementSerializer}


def approve_deny_request_cart(self, request, pk, request_cart_type):
    request_cart_to_approve_deny = get_or_not_found(RequestCart,pk=pk)
    log_action = ActionEnum.REQUEST_APPROVED if request_cart_type == "approved" else ActionEnum.REQUEST_DENIED
    if modify_request_cart_logic.can_approve_disburse_request_cart(request_cart_to_approve_deny,
                                                                   request_cart_type):
        request_cart_to_approve_deny.status = request_cart_type
        serializer = ApproveDenySerializer(request_cart_to_approve_deny, data=request.data)
        if serializer.is_valid():
            serializer.save(staff=request.user, staff_timestamp=datetime.now())
            if request_cart_type == "approved":
                modify_request_cart_logic.subtract_item_in_cart(request_cart_to_approve_deny)
            comment = "{action}: {item_count} items".format(action=log_action.value,
                                                            item_count=serializer.instance.cart_disbursements.count())
            LoggerUtility.log(initiating_user=request.user, nature_enum=log_action,
                              affected_user=request_cart_to_approve_deny.owner,
                              carts_affected=[request_cart_to_approve_deny], comment=comment)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        raise MethodNotAllowed(self.patch, detail="Request cannot be " + request_cart_type)


class ApproveRequestCart(APIView):
    permission_classes = [IsStaffUser]

    def patch(self, request, pk, format=None):
        return approve_deny_request_cart(self, request, pk, "approved")


class CancelRequestCart(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk, format=None):
        request_cart_to_cancel = get_or_not_found(RequestCart, pk=pk)
        if modify_request_cart_logic.can_modify_cart_status(request_cart_to_cancel):
            request_cart_to_cancel.status = "cancelled"
            # reason is guaranteed to not be null since it is required in a request
            if request.data.get('comment') is not None:
                request_cart_to_cancel.reason = "{old_reason} cancellation reason is : {new_reason}"\
                    .format(old_reason=request_cart_to_cancel.reason, new_reason=request.data.get('comment'))
            request_cart_to_cancel.save()
            LoggerUtility.log(initiating_user=request.user, nature_enum=ActionEnum.REQUEST_CANCELLED,
                              affected_user=request.user, carts_affected=[request_cart_to_cancel])
            updated_cart = RequestCart.objects.get(pk=request_cart_to_cancel.id)
            return Response(data=RequestCartSerializer(updated_cart).data, status=status.HTTP_200_OK)
        else:
            raise MethodNotAllowed(self.patch, detail="Cannot cancel request")


class DenyRequestCart(APIView):
    permission_classes = [IsStaffUser]

    def patch(self, request, pk, format=None):
        return approve_deny_request_cart(self, request, pk, "denied")


class FulfillRequestCart(APIView):
    permission_classes = [IsStaffUser]

    def patch(self, request, pk):
        request_cart = get_or_not_found(RequestCart, pk=pk)
        if request_cart.status == 'approved':
            request_cart.status = 'fulfilled'
            start_loan(request_cart)
            request_cart.save()
            LoggerUtility.log(initiating_user=request_cart.staff, nature_enum=ActionEnum.REQUEST_FULFILLED,
                              affected_user=request_cart.owner, carts_affected=[request_cart])
            return Response(data=RequestCartSerializer(request_cart).data, status=status.HTTP_200_OK)
        raise MethodNotAllowed(method=self.patch, detail="Request must be approved but is currently {current_status}"
                               .format(current_status=request_cart.status))


class DispenseRequestCart(generics.UpdateAPIView):
    permission_classes = [IsStaffUser]
    serializer_class = StaffDisburseSerializer
    queryset = RequestCart.objects.all()

    def patch(self, request, *args, **kwargs):
        request.data['status'] = 'fulfilled'
        self.partial_update(request, *args, **kwargs)
        updated_request = self.get_object()
        LoggerUtility.log(initiating_user=updated_request.staff, nature_enum=ActionEnum.ITEMS_DISBURSED,
                          affected_user=updated_request.owner, carts_affected=[updated_request])
        return Response(data=RequestCartSerializer(updated_request).data, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        raise MethodNotAllowed(method=self.put, detail="Only PATCH is supported")

    def perform_update(self, serializer):
        request_cart = self.get_object()
        get_or_not_found(User, pk=serializer.validated_data.get('owner_id'))
        if not modify_request_cart_logic.can_approve_disburse_request_cart(request_cart, 'disburse'):
            detail_str = 'Cannot disburse due to insufficient items' if request_cart.status == 'active' else \
                'Cart needs to be active'
            raise MethodNotAllowed(method=self.patch, detail=detail_str)
        modify_request_cart_logic.subtract_item_in_cart(request_cart)
        start_loan(request_cart)
        serializer.save(staff_timestamp=datetime.now())


class ModifyQuantityRequested(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        serializer = QuantitySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        type_request_to_change = get_or_not_found(TYPE_MAP.get(serializer.validated_data['type']), pk=pk)
        if type_request_to_change.cart.status != 'active':
            raise MethodNotAllowed(self.patch, "Item with quantity to modify must be part of active cart")
        type_request_to_change.quantity = serializer.validated_data['quantity']
        type_request_to_change.save()
        return Response(data=SERIALIZER_MAP.get(serializer.validated_data['type'])(type_request_to_change).data,
                        status=status.HTTP_200_OK)











