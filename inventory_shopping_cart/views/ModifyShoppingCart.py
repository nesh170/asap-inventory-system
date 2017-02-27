from datetime import datetime

from rest_framework import status
from rest_framework.exceptions import MethodNotAllowed, NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from inventoryProject.permissions import IsStaffUser
from inventory_shopping_cart.business_logic import modify_shopping_cart_logic
from inventory_shopping_cart.models import ShoppingCart
from inventory_shopping_cart.serializers.CancelSerializer import CancelSerializer
from inventory_shopping_cart.serializers.ShoppingCartSerializer import ShoppingCartSerializer
from inventory_shopping_cart.serializers.StatusSerializer import StatusSerializer
from inventory_transaction_logger.action_enum import ActionEnum
from inventory_transaction_logger.utility.logger import LoggerUtility


def approve_deny_shopping_cart(self, request, pk, shopping_cart_type):
    shopping_cart_to_approve_deny = get_shopping_cart(pk)
    if shopping_cart_type == "approved":
        log_action = ActionEnum.REQUEST_APPROVED
    else:
        log_action = ActionEnum.REQUEST_DENIED
    if modify_shopping_cart_logic.can_approve_deny_cancel_shopping_cart(shopping_cart_to_approve_deny, shopping_cart_type):
        shopping_cart_to_approve_deny.status = shopping_cart_type
        serializer = StatusSerializer(shopping_cart_to_approve_deny, data=request.data)
        if serializer.is_valid():
            serializer.save(admin=request.user, admin_timestamp=datetime.now())
            if shopping_cart_type == "approved":
                modify_shopping_cart_logic.approve_shopping_cart(shopping_cart_to_approve_deny)
            comment = "{action}: {item_count} items".format(action=log_action.value,
                                                            item_count=serializer.instance.requests.count())
            LoggerUtility.log(initiating_user=request.user, nature_enum=log_action,
                              affected_user=shopping_cart_to_approve_deny.owner,
                              carts_affected=[shopping_cart_to_approve_deny], comment=comment)
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
    permission_classes = [IsStaffUser]

    def patch(self, request, pk, format=None):
        return approve_deny_shopping_cart(self, request, pk, "approved")


class CancelShoppingCart(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk, format=None):
        shopping_cart_to_cancel = get_shopping_cart(pk)
        if modify_shopping_cart_logic.can_approve_deny_cancel_shopping_cart(shopping_cart_to_cancel, "cancelled"):
            shopping_cart_to_cancel.status = "cancelled"
            # reason is guaranteed to not be null since it is required in a request
            if request.data.get('comment') is not None:
                shopping_cart_to_cancel.reason = shopping_cart_to_cancel.reason + " cancellation reason is : " + request.data.get('comment')
            serializer = CancelSerializer(shopping_cart_to_cancel, data=request.data)
            if serializer.is_valid():
                serializer.save()
                LoggerUtility.log(initiating_user=request.user, nature_enum=ActionEnum.REQUEST_CANCELLED,
                                  affected_user=request.user, carts_affected=[shopping_cart_to_cancel])
                updated_cart = ShoppingCart.objects.get(pk=shopping_cart_to_cancel.id)
                serializer_cart = ShoppingCartSerializer(updated_cart)
                return Response(serializer_cart.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            raise MethodNotAllowed(self.patch, detail="Cannot cancel request")


class DenyShoppingCart(APIView):
    permission_classes = [IsStaffUser]

    def patch(self, request, pk, format=None):
        return approve_deny_shopping_cart(self, request, pk, "denied")
