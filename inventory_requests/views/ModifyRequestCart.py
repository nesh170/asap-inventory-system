from datetime import datetime

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import generics
from rest_framework import status
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from inventoryProject.permissions import IsStaffUser
from inventoryProject.utility.queryset_functions import get_or_not_found
from inventory_email_support.utility.email_utility import EmailUtility
from inventory_requests.business_logic import modify_request_cart_logic
from inventory_requests.business_logic.modify_request_cart_logic import start_loan
from inventory_requests.models import RequestCart, Disbursement, Loan
from inventory_requests.serializers.DisbursementSerializer import LoanSerializer, DisbursementSerializer
from inventory_requests.serializers.RequestCartSerializer import RequestCartSerializer, QuantitySerializer, \
    RequestTypeSerializer
from inventory_requests.serializers.RequestStatusSerializer import ApproveDenySerializer, StaffDisburseSerializer, \
    CancelSerializer
from inventory_transaction_logger.action_enum import ActionEnum
from inventory_transaction_logger.utility.logger import LoggerUtility

TYPE_MAP = {'loan': Loan, 'disbursement': Disbursement}
SERIALIZER_MAP = {'loan': LoanSerializer, 'disbursement': DisbursementSerializer}


class ApproveRequestCart(APIView):
    permission_classes = [IsStaffUser]

    def patch(self, request, pk, format=None):
        request_cart_to_approve = get_or_not_found(RequestCart, pk=pk)
        if modify_request_cart_logic.can_approve_disburse_request_cart(request_cart_to_approve):
            request_cart_to_approve.status = "approved"
            serializer = ApproveDenySerializer(request_cart_to_approve, data=request.data)
            if serializer.is_valid():
                serializer.save(staff=request.user, staff_timestamp=datetime.now())
                modify_request_cart_logic.subtract_item_in_cart(request_cart_to_approve)
                comment = "Request Approved: {item_count} items"\
                    .format(item_count=serializer.instance.cart_disbursements.count())
                LoggerUtility.log(initiating_user=request.user, nature_enum=ActionEnum.REQUEST_APPROVED,
                                  affected_user=request_cart_to_approve.owner,
                                  carts_affected=[request_cart_to_approve], comment=comment)
                EmailUtility.email(recipient=request_cart_to_approve.owner.email, template='request_action',
                                   context={'name': request_cart_to_approve.owner.username,
                                            'loan_list': request_cart_to_approve.cart_loans.all(),
                                            'disbursement_list': request_cart_to_approve.cart_disbursements.all(),
                                            'request_state': 'approved'},
                                   subject="Request Approved")
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            raise MethodNotAllowed(self.patch, detail="Request cannot be Approved")


class CancelRequestCart(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CancelSerializer

    def get_queryset(self):
        return RequestCart.objects.filter(owner=self.request.user)

    def perform_update(self, serializer):
        request_cart = self.get_object()
        if modify_request_cart_logic.can_modify_cart_status(request_cart):
            if serializer.validated_data.get('comment') is not None:
                comment_str = "{old_reason} cancellation reason is : {new_reason}"\
                    .format(old_reason=request_cart.reason, new_reason=serializer.validated_data.get('comment'))
            else:
                comment_str = request_cart.reason
            serializer.save(status='cancelled', reason=comment_str)
            LoggerUtility.log(initiating_user=request_cart.owner, nature_enum=ActionEnum.REQUEST_CANCELLED,
                              affected_user=request_cart.owner, carts_affected=[request_cart])
            EmailUtility.email(recipient=request_cart.owner.email, template='request_action',
                               context={'name': request_cart.owner.username,
                                        'loan_list': request_cart.cart_loans.all(),
                                        'disbursement_list': request_cart.cart_disbursements.all(),
                                        'request_state': 'cancelled'},
                               subject="Request Cancelled")
        else:
            raise MethodNotAllowed(method=self.patch, detail="Cart status does not allow cancellation")

    def patch(self, request, *args, **kwargs):
        self.partial_update(request, *args, **kwargs)
        return Response(data=RequestCartSerializer(self.get_object()).data, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        raise MethodNotAllowed(method=self.put, detail="Only Patch is allowed")


class DenyRequestCart(generics.UpdateAPIView):
    permission_classes = [IsStaffUser]
    serializer_class = ApproveDenySerializer
    queryset = RequestCart.objects.all()

    def perform_update(self, serializer):
        request_cart = self.get_object()
        if modify_request_cart_logic.can_modify_cart_status(request_cart):
            comment = "Request Denied: {item_count} items"\
                .format(item_count=serializer.instance.cart_disbursements.count())
            LoggerUtility.log(initiating_user=self.request.user, nature_enum=ActionEnum.REQUEST_DENIED,
                              affected_user=request_cart.owner,
                              carts_affected=[request_cart], comment=comment)
            EmailUtility.email(recipient=request_cart.owner.email, template='request_action',
                               context={'name': request_cart.owner.username,
                                        'loan_list': request_cart.cart_loans.all(),
                                        'disbursement_list': request_cart.cart_disbursements.all(),
                                        'request_state': 'denied'},
                               subject="Request Denied")
            serializer.save(staff=self.request.user, staff_timestamp=datetime.now(), status="denied")
        else:
            raise MethodNotAllowed(method=self.patch, detail="Cart status does not allow denying")

    def put(self, request, *args, **kwargs):
        raise MethodNotAllowed(method=self.put, detail="Only Patch is allowed")


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

        EmailUtility.email(recipient=updated_request.owner.email, template='items_dispensed',
                           context={'name': updated_request.owner.username,
                                    'loan_list': updated_request.cart_loans.all(),
                                    'disbursement_list': updated_request.cart_disbursements.all()},
                           subject="Items Dispensed")

        return Response(data=RequestCartSerializer(updated_request).data, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        raise MethodNotAllowed(method=self.put, detail="Only PATCH is supported")

    def perform_update(self, serializer):
        request_cart = self.get_object()
        get_or_not_found(User, pk=serializer.validated_data.get('owner_id'))
        if not modify_request_cart_logic.can_approve_disburse_request_cart(request_cart):
            detail_str = 'Cannot dispense due to insufficient items' if request_cart.status == 'active' else \
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


class ConvertRequestType(APIView):
    permission_classes = [IsStaffUser]

    def post(self, request, format=None):
        serializer = RequestTypeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        old_type = serializer.validated_data['current_type']
        request_type = get_or_not_found(TYPE_MAP.get(old_type), pk=serializer.validated_data['pk'])
        if modify_request_cart_logic.can_convert_request_type(request_type.cart, request.user):
            args = {'item': request_type.item, 'cart': request_type.cart}
            new_type = 'loan' if old_type != 'loan' else 'disbursement'
            try:
                # this case is when there is a request_type for that item already, just add quantity
                new_request_type = TYPE_MAP.get(new_type).objects.get(**args)
                new_request_type.quantity = new_request_type.quantity + request_type.quantity
            except ObjectDoesNotExist:
                new_request_type = TYPE_MAP.get(new_type).objects.create(quantity=request_type.quantity, **args)
                # this case is when it is already disbursed out and the manager wants to convert it to a loan
                if new_request_type.cart.status == 'fulfilled' and new_type == 'loan':
                    new_request_type.loaned_timestamp = request_type.cart.staff_timestamp
            new_request_type.save()
            request_type.delete()
            EmailUtility.email(recipient=request_type.cart.owner.email, template='convert_loan_to_disbursement',
                               context={'name': request_type.cart.owner.username, 'item_name': request_type.item.name,
                                        'quantity': request_type.quantity}, subject="Loan Conversion to Disbursement")

            return Response(data=SERIALIZER_MAP.get(new_type)(new_request_type).data, status=status.HTTP_201_CREATED)
        raise MethodNotAllowed(method=self.post, detail="Cannot change request_type due to cart_status {status}"
                               .format(status=request_type.cart.status))
