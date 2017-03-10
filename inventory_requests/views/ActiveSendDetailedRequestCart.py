from rest_framework import status
from rest_framework.exceptions import MethodNotAllowed, NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from inventory_requests.models import RequestCart
from inventory_requests.serializers.RequestCartSerializer import RequestCartSerializer
from inventory_transaction_logger.action_enum import ActionEnum
from inventory_transaction_logger.utility.logger import LoggerUtility


def get_request_cart(pk):
    try:
        return RequestCart.objects.get(pk=pk)
    except RequestCart.DoesNotExist:
        raise NotFound(detail="Request Cart not found")


class ViewDetailedRequestCart(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk, format=None):
        request_cart = get_request_cart(pk)
        serializer = RequestCartSerializer(request_cart)
        return Response(serializer.data)


class ActiveRequestCart(APIView):
    permission_classes = [IsAuthenticated]

    def get_active(self):
        user = self.request.user
        try:
            return RequestCart.objects.filter(owner=user).get(status='active')
        except RequestCart.DoesNotExist:
            new_request_cart = RequestCart.objects.create(owner=user, status='active')
            return new_request_cart

    def get(self, request, format=None):
        request_cart = self.get_active()
        serializer = RequestCartSerializer(request_cart)
        return Response(serializer.data)


class SendCart(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk, format=None):
        request_cart = get_request_cart(pk)
        if request_cart.cart_disbursements.count() == 0:
            raise MethodNotAllowed(detail="Cannot submit empty request cart", method=self.patch)
        if request_cart.status == "active":
            request_cart.status = "outstanding"
            serializer = RequestCartSerializer(request_cart, data=request.data)
            if serializer.is_valid():
                serializer.save()
                LoggerUtility.log(initiating_user=request.user, nature_enum=ActionEnum.REQUEST_CREATED,
                                  carts_affected=[request_cart])
                return Response(serializer.data)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            raise MethodNotAllowed(self.patch, "Cannot send this request cart because status is not active")