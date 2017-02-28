from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import generics
from rest_framework.exceptions import MethodNotAllowed, NotFound, ParseError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from inventoryProject.permissions import IsStaffOrReadOnly, IsStaffUser
from inventoryProject.utility.queryset_functions import get_or_none
from inventory_disbursements.business_logic.quantity_logic import quantity_logic
from inventory_disbursements.models import Cart, Disbursement
from inventory_disbursements.serializers.disbursement_serializer import CartSerializer, DisbursementSerializer
from inventory_transaction_logger.action_enum import ActionEnum
from inventory_transaction_logger.utility.logger import LoggerUtility
from items.models import Item


class CartList(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CartSerializer

    def get_queryset(self):
        return Cart.objects.all() if self.request.user.is_staff else \
            Cart.objects.filter(receiver=self.request.user)


class DisbursementCreation(generics.CreateAPIView):
    permission_classes = [IsStaffUser]
    serializer_class = DisbursementSerializer
    queryset = Disbursement.objects.all()

    def perform_create(self, serializer):
        item = get_or_none(Item, pk=serializer.validated_data.get('item_id'))
        cart = get_or_none(Cart, pk=serializer.validated_data.get('cart_id'))
        quantity = serializer.validated_data.get('quantity')
        if item is None:
            raise NotFound('Item is not found in database')
        if cart is None:
            raise NotFound('Cart is not found in database')
        if cart.receiver is not None:
            raise MethodNotAllowed(detail="The cart needs to be active", method=self.perform_create)
        if cart.disbursements.filter(item=item).exists():
            raise MethodNotAllowed(detail="Item is already in cart", method=self.perform_create)
        quantity_logic(quantity=quantity, item_quantity=item.quantity, method=self.perform_create)
        serializer.save()


class DisbursementUpdateDeletion(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsStaffUser]
    serializer_class = DisbursementSerializer
    queryset = Disbursement.objects.all()

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.cart.receiver is not None:
            raise MethodNotAllowed(detail='You can only modify an active Disbursement Cart', method=self.destroy)
        return self.destroy(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.cart.receiver is not None:
            raise MethodNotAllowed(detail='You can only modify an active Disbursement Cart', method=self.patch)
        return self.partial_update(request, *args, **kwargs)

    def perform_update(self, serializer):
        disbursement = self.get_object()
        quantity = serializer.validated_data.get('quantity')
        quantity_logic(quantity=quantity, item_quantity=disbursement.item.quantity, method=self.perform_update)
        serializer.save()


class ActiveCart(APIView):
    permission_classes = [IsStaffUser]

    def get(self, request):
        try:
            cart = Cart.objects.get(disburser=request.user, receiver=None)
        except ObjectDoesNotExist:
            cart = Cart.objects.create(disburser=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)


def subtract_item_quantity(disbursement):
    item = disbursement.item
    item.quantity -= disbursement.quantity
    item.save()


def precheck_item_quantity(disbursement):
    item = disbursement.item
    if disbursement.quantity > item.quantity:
        error_str = "Item {item} has quantity {quantity} but needs to disburse {disburse_quantity}".format
        raise MethodNotAllowed(detail=error_str(item=item.name, quantity=item.quantity,
                                                disburse_quantity=disbursement.quantity), method=precheck_item_quantity)


class CartSubmission(generics.RetrieveUpdateAPIView):
    permission_classes = [IsStaffOrReadOnly]
    serializer_class = CartSerializer

    def get_queryset(self):
        return Cart.objects.all() if self.request.user.is_staff else \
            Cart.objects.filter(receiver=self.request.user)

    def perform_update(self, serializer):
        if serializer.validated_data.get('receiver_id') is None:
            raise ParseError("receiver_id is required to submit a cart")
        user = get_or_none(User, pk=serializer.validated_data.get('receiver_id'))
        if user is None:
            raise NotFound("User is not found in database")
        if serializer.instance.receiver is not None:
            raise MethodNotAllowed(detail="This cart has been disbursed", method=self.perform_update)
        disbursements = Disbursement.objects.filter(cart_id=serializer.instance.id)
        if disbursements.count() == 0:
            raise MethodNotAllowed(detail="This cart is empty so it cannot be submitted", method=self.perform_update)
        [precheck_item_quantity(disbursement) for disbursement in disbursements]
        [subtract_item_quantity(disbursement) for disbursement in disbursements]
        serializer.save()
        comment_string = "Disbursed {number} items".format
        comment = comment_string(number=Disbursement.objects.filter(cart_id=serializer.instance.id).count())
        LoggerUtility.log(initiating_user=self.request.user, nature_enum=ActionEnum.ITEMS_DISBURSED,
                          comment=comment, affected_user=user, disbursement_affected=[self.get_object()])