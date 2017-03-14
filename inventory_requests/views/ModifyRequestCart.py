from datetime import datetime

from rest_framework import status
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from inventoryProject.permissions import IsStaffUser
from inventoryProject.utility.queryset_functions import get_or_not_found
from inventory_requests.business_logic import modify_request_cart_logic
from inventory_requests.models import RequestCart
from inventory_requests.serializers.ApproveDenySerializer import ApproveDenySerializer
from inventory_requests.serializers.RequestCartSerializer import RequestCartSerializer
from inventory_transaction_logger.action_enum import ActionEnum
from inventory_transaction_logger.utility.logger import LoggerUtility


def approve_deny_request_cart(self, request, pk, request_cart_type):
    request_cart_to_approve_deny = get_or_not_found(RequestCart,pk=pk)
    log_action = ActionEnum.REQUEST_APPROVED if request_cart_type == "approved" else ActionEnum.REQUEST_DENIED
    if modify_request_cart_logic.can_approve_deny_cancel_disburse_request_cart(request_cart_to_approve_deny,
                                                                               request_cart_type):
        request_cart_to_approve_deny.status = request_cart_type
        serializer = ApproveDenySerializer(request_cart_to_approve_deny, data=request.data)
        if serializer.is_valid():
            serializer.save(staff=request.user, staff_timestamp=datetime.now())
            if request_cart_type == "approved":
                modify_request_cart_logic.approve_request_cart(request_cart_to_approve_deny)
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
        if modify_request_cart_logic.can_approve_deny_cancel_disburse_request_cart(request_cart_to_cancel, "cancelled"):
            request_cart_to_cancel.status = "cancelled"
            # reason is guaranteed to not be null since it is required in a request
            if request.data.get('comment') is not None:
                request_cart_to_cancel.reason = "{old_reason} cancellation reason is : {new_reason}"\
                    .format(old_reason=request_cart_to_cancel.reason, new_reason=request.data.get('comment'))
            request_cart_to_cancel.save()
            LoggerUtility.log(initiating_user=request.user, nature_enum=ActionEnum.REQUEST_CANCELLED,
                              affected_user=request.user, carts_affected=[request_cart_to_cancel])
            updated_cart = RequestCart.objects.get(pk=request_cart_to_cancel.id)
            serializer_cart = RequestCartSerializer(updated_cart)
            return Response(data=serializer_cart.data, status=status.HTTP_200_OK)
        else:
            raise MethodNotAllowed(self.patch, detail="Cannot cancel request")


class DenyRequestCart(APIView):
    permission_classes = [IsStaffUser]

    def patch(self, request, pk, format=None):
        return approve_deny_request_cart(self, request, pk, "denied")


