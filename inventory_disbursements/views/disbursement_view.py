from django.core.exceptions import ObjectDoesNotExist
from rest_framework import generics
from rest_framework.exceptions import MethodNotAllowed, NotFound
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from inventoryProject.utility.queryset_functions import get_or_none
from inventory_disbursements.models import Cart, Disbursement
from inventory_disbursements.serializers.disbursement_serializer import CartSerializer, DisbursementSerializer
from items.models import Item


class CartList(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CartSerializer

    def get_queryset(self):
        return Cart.objects.all() if self.request.user.is_staff else \
            Cart.objects.filter(receiver=self.request.user)


class DisbursementCreation(generics.CreateAPIView):
    permission_classes = [IsAdminUser]
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
            raise MethodNotAllowed(detail="Item is already in database", method=self.perform_create)
        if quantity >= item.quantity:
            raise MethodNotAllowed(detail="Quantity to be disbursed is more than item value", method=self.perform_create)
        serializer.save()


class DisbursementDeletion(generics.DestroyAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = DisbursementSerializer
    queryset = Disbursement.objects.all()

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.cart.receiver is not None:
            raise MethodNotAllowed(detail='You can only modify an active Disbursement Cart', method=self.destroy)
        return self.destroy(request, *args, **kwargs)


class ActiveCart(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        try:
            cart = Cart.objects.get(disburser=request.user, receiver=None)
        except ObjectDoesNotExist:
            print('created new cart')
            cart = Cart.objects.create(disburser=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)


class CartSubmission(generics.UpdateAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = CartSerializer
    queryset = Cart.objects.all()

    def perform_update(self, serializer):
        if serializer.instance.receiver is not None:
            raise MethodNotAllowed(detail="This cart has been disbursed", method=self.perform_update)
        serializer.save()





