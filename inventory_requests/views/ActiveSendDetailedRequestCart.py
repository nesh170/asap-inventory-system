from django.db.models import Q
from rest_framework import status
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from inventoryProject.utility.queryset_functions import get_or_not_found
from inventory_email_support.utility.email_utility import EmailUtility
from inventory_requests.models import RequestCart
from inventory_requests.serializers.RequestCartSerializer import RequestCartSerializer
from inventory_transaction_logger.action_enum import ActionEnum
from inventory_transaction_logger.utility.logger import LoggerUtility


class ViewDetailedRequestCart(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk, format=None):
        request_cart = get_or_not_found(RequestCart, pk=pk)
        serializer = RequestCartSerializer(request_cart)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ActiveRequestCart(APIView):
    permission_classes = [IsAuthenticated]

    def get_active(self):
        user = self.request.user
        q_func = Q(staff=user) if user.is_staff else Q(owner=user)
        try:
            return RequestCart.objects.get(q_func, status='active')
        except RequestCart.DoesNotExist:
            new_request_cart = RequestCart.objects.create(staff=user, status='active') if user.is_staff else \
                RequestCart.objects.create(owner=user, status='active')
            return new_request_cart

    def get(self, request, format=None):
        request_cart = self.get_active()
        serializer = RequestCartSerializer(request_cart)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SendCart(APIView):
    permission_classes = [IsAuthenticated]

    def request_backfills(self, cart_loans):
        for loan in cart_loans.all():
            if loan.backfill_loan.filter(status='backfill_active').exists():
                active_backfill = loan.backfill_loan.get(status='backfill_active')
                if active_backfill.quantity > loan.quantity:
                    raise MethodNotAllowed(method=self.patch, detail="Cannot backfill a quantity greater than the "
                                                                     "current amount for loan")
                active_backfill.status = 'backfill_request'
                active_backfill.save()

    def patch(self, request, pk, format=None):
        request_cart = get_or_not_found(RequestCart, pk=pk)
        if request_cart.owner is None and request_cart.staff is not None:
            raise MethodNotAllowed(detail="This is a Staff Cart, please use the dispense method", method=self.patch)
        if request_cart.cart_disbursements.count() == 0 and request_cart.cart_loans.count() == 0:
            raise MethodNotAllowed(detail="Cannot submit empty request cart", method=self.patch)
        if request_cart.status == "active":
            request_cart.status = "outstanding"
            self.request_backfills(request_cart.cart_loans)
            serializer = RequestCartSerializer(request_cart, data=request.data)
            if serializer.is_valid():
                serializer.save()
                LoggerUtility.log(initiating_user=request.user, nature_enum=ActionEnum.REQUEST_CREATED,
                                  carts_affected=[request_cart])
                EmailUtility.email(recipient=request_cart.owner.email, template='request_action',
                                   context={'name': request_cart.owner.username,
                                            'loan_list': request_cart.cart_loans.all(),
                                            'disbursement_list': request_cart.cart_disbursements.all(),
                                            'request_state': 'created'},
                                   subject="Request Created")
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            raise MethodNotAllowed(self.patch, "Cannot send this request cart because status is not active")