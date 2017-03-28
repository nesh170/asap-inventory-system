import django_filters
from django.db.models import Q
from rest_framework import generics
from rest_framework import status
from rest_framework.exceptions import MethodNotAllowed, ParseError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from inventoryProject.permissions import IsStaffUser
from inventoryProject.utility.queryset_functions import get_or_not_found
from inventory_email_support.utility.email_utility import EmailUtility
from inventory_requests.business_logic.loan_logic import return_loan_logic
from inventory_requests.models import Loan, RequestCart
from inventory_requests.serializers.DisbursementSerializer import LoanSerializer
from inventory_requests.serializers.RequestCartSerializer import RequestCartSerializer
from inventory_transaction_logger.action_enum import ActionEnum
from inventory_transaction_logger.utility.logger import LoggerUtility


class CreateLoan(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LoanSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filter_fields = ('cart__status', 'item__name', 'cart__owner__username')

    def get_queryset(self):
        user = self.request.user
        returned = self.request.query_params.get('returned', None)
        q_func = ~Q(pk=None) and Q(returned_timestamp__isnull=not (returned == 'true')) if returned else ~Q(pk=None)
        q_func = q_func if user.is_staff else q_func and Q(cart__owner=user)
        return Loan.objects.filter(q_func)


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
        try:
            quantity = int(request.data.get('quantity'))
        except ValueError:
            raise ParseError('This is not valid quantity')
        except TypeError:
            quantity = None
        if quantity is not None and (quantity < 1 or quantity > loan.quantity):
            detail_str = "Quantity {quantity} cannot be greater than loan quantity({loan_q}) or less than 1"\
                .format(quantity=quantity, loan_q=loan.quantity)
            raise MethodNotAllowed(self.patch, detail=detail_str)
        if loan.cart.status == 'fulfilled' and return_loan_logic(loan=loan, quantity=quantity):
            EmailUtility.email(recipient=loan.cart.owner.email, template='return_loan',
                               context={'name': loan.cart.owner.username,
                                        'item_name': loan.item.name,
                                        'quantity': quantity},
                               subject="Loaned Item Returned")
            updated_loan = Loan.objects.get(pk=loan.id)
            comment_str = "{quantity} out of {quantity_loaned} lent has been returned of {item}"\
                .format(quantity=updated_loan.returned_quantity, quantity_loaned=updated_loan.quantity,
                        item=updated_loan.item.name)
            LoggerUtility.log(initiating_user=request.user, nature_enum=ActionEnum.LOAN_RETURNED, comment=comment_str,
                              affected_user=updated_loan.cart.owner, carts_affected=[updated_loan.cart])
            return Response(data=LoanSerializer(updated_loan).data, status=status.HTTP_200_OK)
        user_name = loan.cart.owner.username if loan.cart.owner is not None else "NO USER"
        detail_str = "Request needs to be fulfilled but is {status} and {item_name} cannot be " \
                     "returned already by {user_name} and returned loan quantity is {returned_quantity} " \
                     "and quantity is {quantity}"\
            .format(status=loan.cart.status, item_name=loan.item.name, user_name=user_name,
                    returned_quantity=loan.returned_quantity, quantity=loan.quantity)
        raise MethodNotAllowed(method=self.patch, detail=detail_str)


class ReturnAllLoans(APIView):
    permission_classes = [IsStaffUser]

    def patch(self, request, pk):
        cart = get_or_not_found(RequestCart, pk=pk)
        if cart.status == 'fulfilled' and cart.cart_loans.filter(returned_timestamp__isnull=True).exists():
            [return_loan_logic(loan=loan) for loan in cart.cart_loans.all()]
            updated_cart = get_or_not_found(RequestCart, pk=pk)
            EmailUtility.email(recipient=cart.owner.email, template='return_all_loans',
                               context={'name': cart.owner.username,
                                        'loan_list': cart.cart_loans.all()},
                               subject="Loaned Items Returned")
            LoggerUtility.log(initiating_user=request.user, nature_enum=ActionEnum.LOAN_RETURNED,
                              affected_user=cart.owner, carts_affected=[cart])
            return Response(data=RequestCartSerializer(updated_cart).data, status=status.HTTP_200_OK)
        detail_str = "Request needs to be fulfilled but is {status} or Cart has been fully returned"\
            .format(status=cart.status)
        raise MethodNotAllowed(method=self.patch, detail=detail_str)

