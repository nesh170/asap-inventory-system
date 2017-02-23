from rest_framework.exceptions import MethodNotAllowed, NotFound
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from inventory_shopping_cart.business_logic import modify_shopping_cart_logic
from inventory_shopping_cart.serializers import StatusSerializer, CancelSerializer
from datetime import datetime
from inventory_logger.utility.logger import LoggerUtility
from inventory_logger.action_enum import ActionEnum
from inventory_shopping_cart.models import ShoppingCart

def approveDenyShoppingCart(self, request, pk, shopping_cart_type):
    shopping_cart_to_approve_deny = get_shopping_cart(pk)
    if (shopping_cart_type == "approved"):
        type_for_comment = "approval"
        log_action = ActionEnum.REQUEST_APPROVED
    else:
        type_for_comment = "denial"
        log_action = ActionEnum.REQUEST_DENIED
    if modify_shopping_cart_logic.can_approve_deny_cancel_shopping_cart(shopping_cart_to_approve_deny, shopping_cart_type):
        shopping_cart_to_approve_deny.status = shopping_cart_type
        if (shopping_cart_to_approve_deny.admin_comment is not None):
            if (request.data.get('admin_comment') is not None):
                request.data[
                    'admin_comment'] = shopping_cart_to_approve_deny.admin_comment + " " + type_for_comment + " reason is : " + request.data.get(
                    'admin_comment')
            else:
                request.data['admin_comment'] = shopping_cart_to_approve_deny.admin_comment;
        else:
            if (request.data.get('admin_comment') is not None):
                request.data['admin_comment'] = type_for_comment + " reason is : " + request.data.get('admin_comment')
            else:
                request.data['admin_comment'] = None;
        serializer = StatusSerializer.StatusSerializer(shopping_cart_to_approve_deny, data=request.data)
        if serializer.is_valid():
            LoggerUtility.log_as_system(log_action,
                                        "Request (ID: " + str(shopping_cart_to_approve_deny.id) + ") " + shopping_cart_type)
            serializer.save(admin=request.user, admin_timestamp=datetime.now())
            if shopping_cart_type == "approved":
                modify_shopping_cart_logic.approve_shopping_cart(shopping_cart_to_approve_deny)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        raise MethodNotAllowed(self.patch, detail="Request cannot be " + shopping_cart_type)


def get_shopping_cart(pk):
    try:
        return ShoppingCart.objects.get(pk=pk)
    except ShoppingCart.DoesNotExist:
        raise NotFound(detail="Shopping Cart not found")
class ApproveShoppingCart(APIView):
   permission_classes = [IsAdminUser]
   def patch(self, request, pk, format=None):
       return approveDenyShoppingCart(self, request, pk, "approved")

class CancelShoppingCart(APIView):
    permission_classes = [IsAuthenticated]
    def patch(self, request, pk, format=None):
        shopping_cart_to_cancel = get_shopping_cart(pk)
        if modify_shopping_cart_logic.can_approve_deny_cancel_shopping_cart(shopping_cart_to_cancel, "cancelled"):
            shopping_cart_to_cancel.status = "cancelled"
            #reason is guaranteed to not be null since it is required in a request
            if (request.data.get('reason') is not None):
                request.data['reason'] = shopping_cart_to_cancel.reason + " cancellation reason is : " + request.data.get('reason')
            else:
                request.data['reason'] = shopping_cart_to_cancel.reason
            serializer = CancelSerializer.CancelSerializer(shopping_cart_to_cancel, data=request.data)
            if serializer.is_valid():
                LoggerUtility.log_as_system(ActionEnum.REQUEST_CANCELLED, "Request (ID: " + str(shopping_cart_to_cancel.id) + ") Cancelled")
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            raise MethodNotAllowed(self.patch, detail="Cannot cancel request")


class DenyShoppingCart(APIView):
    permission_classes = [IsAdminUser]
    def patch(self, request, pk, format=None):
        return approveDenyShoppingCart(self, request, pk, "denied")