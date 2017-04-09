from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from inventoryProject.permissions import IsStaffUser
from inventory_email_support.utility.email_utility import EmailUtility
from inventory_requests.serializers.RequestCartSerializer import RequestCartSerializer
from inventory_requests.serializers.InstantRequestSerializer import InstantRequestSerializer
from inventory_transaction_logger.action_enum import ActionEnum
from inventory_transaction_logger.utility.logger import LoggerUtility


class InstantRequest(APIView):
    permission_classes = [IsStaffUser]

    def post(self, request):
        serializer = InstantRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cart = serializer.save()
        cart.staff = request.user
        cart.save()
        LoggerUtility.log(initiating_user=cart.staff, nature_enum=ActionEnum.ITEMS_DISBURSED,
                          affected_user=cart.owner, carts_affected=[cart])
        EmailUtility.email(recipient=cart.owner.email, template='items_dispensed',
                           context={'name': cart.owner.username,
                                    'loan_list': cart.cart_loans.all(),
                                    'disbursement_list': cart.cart_disbursements.all()},
                           subject="Items Dispensed")
        return Response(status=status.HTTP_200_OK, data=RequestCartSerializer(cart).data)
