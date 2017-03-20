from datetime import datetime

import django_filters
from rest_framework import generics
from rest_framework import status
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from inventoryProject.permissions import IsStaffUser
from inventoryProject.utility.queryset_functions import get_or_not_found
from inventory_requests.business_logic.loan_logic import return_loan_logic
from inventory_requests.models import Loan, RequestCart
from inventory_requests.serializers.DisbursementSerializer import LoanSerializer
from inventory_requests.serializers.RequestCartSerializer import RequestCartSerializer
from items.models import Item


class CreateLoan(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LoanSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filter_fields = ('cart__status',)

    def get_queryset(self):
        user = self.request.user
        return Loan.objects.all() if user.is_staff else Loan.objects.filter(cart__owner=user)


class DeleteLoan(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LoanSerializer
    queryset = Loan.objects.all()

    def perform_destroy(self, instance):
        user = self.request.user
        request = instance.cart
        if request.status == 'active' and (request.owner == user or user.is_staff):
            instance.delete()
        else:
            detail_str = "Cannot delete loan as request status: {status} != active".format(status=request.status)
            raise MethodNotAllowed(method=self.delete, detail=detail_str)


class ReturnLoan(APIView):
    permission_classes = [IsStaffUser]

    def patch(self, request, pk):
        loan = get_or_not_found(Loan, pk=pk)
        quantity = request.data.get('quantity')
        if quantity is not None and (quantity < 1 or quantity > loan.quantity):
            detail_str = "Quantity {quantity} cannot be greater than loan quantity({loan_q}) or less than 1"\
                .format(quantity=quantity, loan_q=loan.quantity)
            raise MethodNotAllowed(self.patch, detail=detail_str)
        if loan.cart.status == 'fulfilled' and return_loan_logic(loan=loan, quantity=quantity):
            return Response(data=LoanSerializer(loan).data, status=status.HTTP_200_OK)
        detail_str = "Request needs to be fulfilled but is {status} and {item_name} cannot be " \
                     "returned already by {user_name}".format(status=loan.cart.status, item_name=loan.item.name,
                                                              user_name=loan.cart.owner.username)
        raise MethodNotAllowed(method=self.patch, detail=detail_str)


class ReturnAllLoans(APIView):
    permission_classes = [IsStaffUser]

    def patch(self, request, pk):
        cart = get_or_not_found(RequestCart, pk=pk)
        if cart.status == 'fulfilled' and cart.cart_loans.filter(returned_timestamp__isnull=True).exists():
            [return_loan_logic(loan=loan) for loan in cart.cart_loans.all()]
            updated_cart = get_or_not_found(RequestCart, pk=pk)
            return Response(data=RequestCartSerializer(updated_cart).data, status=status.HTTP_200_OK)
        detail_str = "Request needs to be fulfilled but is {status} or Cart has been fully returned"\
            .format(status=cart.status)
        raise MethodNotAllowed(method=self.patch, detail=detail_str)

