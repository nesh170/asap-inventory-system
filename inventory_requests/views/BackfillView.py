from datetime import datetime

import boto3
from django.conf import settings
from rest_framework import filters
from rest_framework import generics
from rest_framework import status
from rest_framework.exceptions import MethodNotAllowed, ParseError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from inventoryProject.permissions import IsStaffUser
from inventoryProject.utility.queryset_functions import get_or_not_found
from inventory_email_support.utility.email_utility import EmailUtility
from inventory_requests.models import Loan, Backfill, Disbursement
from inventory_requests.serializers.BackfillSerializer import BackfillSerializer, CreateBackfillSerializer, \
    UpdateBackfillSerializer
from inventory_transaction_logger.action_enum import ActionEnum
from inventory_transaction_logger.utility.logger import LoggerUtility
from items.logic.asset_logic import create_asset_helper


class BackfillList(generics.ListAPIView):
    permission_classes = [IsStaffUser]
    serializer_class = BackfillSerializer
    queryset = Backfill.objects.exclude(status='backfill_active')
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('status',)


def generate_key(file):
    key_str = "{timestamp}{file_name}".format
    return key_str(timestamp=datetime.now(), file_name=file)


def upload_file(file, filename):
    s3 = boto3.resource('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
    key = generate_key(file)
    s3.Bucket('backfillfiles').upload_file(filename, key)
    return 'https://s3.amazonaws.com/backfillfiles/{key}'.format(key=key)

#creates a backfill with status 'backfill_active' when a PDF is uploaded on the cart page. However, when they request
#backfill for a loan that has been fulfilled, it creates a backfill with status 'backfill_request' directly since there
#is no need for an active state
#TODO I'm not sure if this is the desired behavior, it depends on how the UI wants to do it


class CreateBackfillRequest(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        receipt = request.FILES['receipt_pdf'] if 'receipt_pdf' in request.FILES else None
        if receipt is None:
            raise MethodNotAllowed(method=self.post, detail="Please upload a PDF to make the backfill request")
        filename = 'receipt.pdf'
        with open(filename, 'wb+') as temp_file:
            for chunk in receipt.chunks():
                temp_file.write(chunk)
        file_url = upload_file(receipt, filename)
        serializer = CreateBackfillSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        associated_loan = get_or_not_found(Loan, pk=serializer.validated_data.get('loan_id'))
        associated_cart = associated_loan.cart
        #to catch an error when they try creating another backfill request for a loan they already created a backfill
        #for on the cart page
        if associated_loan.backfill_loan.filter(status='backfill_active').exists() and associated_cart.status == 'active':
            raise MethodNotAllowed(method=self.post, detail="Cannot create a backfill request when the current "
                                                            "one hasn't been requested already")
        backfill_request_quantity = serializer.validated_data.get('quantity')
        cart_status = associated_loan.cart.status
        if cart_status not in ('active', 'fulfilled'):
            detail_str = "Cannot create backfill request for the current loan because the corresponding request is" \
                         " {cart_status}".format
            raise MethodNotAllowed(self.post, detail=detail_str(cart_status=cart_status))
        if backfill_request_quantity > associated_loan.quantity:
            raise MethodNotAllowed(method=self.post,
                                   detail="Cannot backfill a quantity greater than the current amount for loan")
        if cart_status == 'fulfilled' and associated_loan.returned_timestamp is not None:
            raise MethodNotAllowed(self.post, "Cannot request backfill because the loan has been fully returned")
        file_name = "{name}".format
        backfill_obj = Backfill.objects.create(loan=associated_loan,
                                quantity=backfill_request_quantity, timestamp=datetime.now(), pdf_url=file_url,
                                               file_name=file_name(name=receipt))
        #for fulfilled cart, want to set it to backfill_request state directly
        if associated_cart.status == 'fulfilled':
            backfill_obj.status = 'backfill_request'
            backfill_obj.save()
            comment_str = "Backfill for quantity {quantity} was created for loaned {item_name}, " \
                      "which is part of request with status {status}".format
            comment = comment_str(quantity=backfill_request_quantity, item_name=associated_loan.item.name,
                              status=cart_status)
            LoggerUtility.log(initiating_user=request.user, nature_enum=ActionEnum.BACKFILL_CREATED,
                          items_affected=[associated_loan.item], comment=comment, carts_affected=[associated_loan.cart])
            EmailUtility.email(recipient=associated_cart.owner.email, template='backfill_create_approve_deny_cancel',
                           context={'name': associated_cart.owner.username,
                                    'backfill_state': 'created',
                                    'item_name': associated_loan.item.name, 'quantity': backfill_obj.quantity},
                           subject="Backfill Request Created")
        return Response(BackfillSerializer(backfill_obj).data, status=status.HTTP_200_OK)


class CancelBackfillRequest(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk, format=None):
        backfill_request_to_cancel = get_or_not_found(Backfill, pk=pk)
        if backfill_request_to_cancel.status != 'backfill_request':
            raise MethodNotAllowed(self.patch, detail="Cannot cancel backfill because it is not in the backfill "
                                                      "request state")
        cart = backfill_request_to_cancel.loan.cart
        #to prevent them from calling this api for a request that is outstanding
        if cart.status == 'outstanding':
            raise MethodNotAllowed(self.patch, detail="Please cancel the entire request if you would like to cancel"
                                                      " this backfill request")
        backfill_request_to_cancel.status = 'backfill_cancelled'
        backfill_request_to_cancel.timestamp = datetime.now()
        backfill_request_to_cancel.save()
        comment_str = "Backfill for quantity {quantity} was cancelled for loaned {item_name}, " \
                      "which is part of request with status {status}".format
        comment = comment_str(quantity=backfill_request_to_cancel.quantity,
                              item_name=backfill_request_to_cancel.loan.item.name, status=cart.status)
        LoggerUtility.log(initiating_user=request.user, nature_enum=ActionEnum.BACKFILL_CANCELLED,
                          affected_user=backfill_request_to_cancel.loan.cart.owner,
                          items_affected=[backfill_request_to_cancel.loan.item], comment=comment,
                          carts_affected=[backfill_request_to_cancel.loan.cart])
        EmailUtility.email(recipient=cart.owner.email, template='backfill_create_approve_deny_cancel',
                           context={'name': cart.owner.username,
                                    'backfill_state': 'cancelled',
                                    'item_name': backfill_request_to_cancel.loan.item.name,
                                    'quantity': backfill_request_to_cancel.quantity},
                           subject="Backfill Request Cancelled")


        return Response(BackfillSerializer(backfill_request_to_cancel).data, status=status.HTTP_200_OK)

class DeleteBackfillRequest(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk, format=None):
        backfill_to_delete = get_or_not_found(Backfill, pk=pk)
        if backfill_to_delete.status != 'backfill_active':
            raise MethodNotAllowed(method=self.delete, detail="Cannot delete a backfill request that is not part of "
                                                              "an active cart")
        backfill_to_delete.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UpdateBackfillRequest(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        serializer = UpdateBackfillSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        backfill_to_update = get_or_not_found(Backfill, pk=serializer.validated_data.get('backfill_id'))
        if backfill_to_update.status != 'backfill_active':
            raise MethodNotAllowed(self.post, detail="Cannot update a backfill request that is not part of an active"
                                                      " cart")
        requested_quantity = serializer.validated_data.get('quantity')
        if requested_quantity is not None:
            if requested_quantity > backfill_to_update.loan.quantity:
                raise MethodNotAllowed(self.post, detail="Cannot backfill a quantity greater than the current amount"
                                                      " for loan")
            backfill_to_update.quantity = requested_quantity
            backfill_to_update.save()
        receipt = request.FILES['receipt_pdf'] if 'receipt_pdf' in request.FILES else None
        if receipt is not None:
            filename = 'receipt.pdf'
            with open(filename, 'wb+') as temp_file:
                for chunk in receipt.chunks():
                    temp_file.write(chunk)
            file_url = upload_file(receipt, filename)
            backfill_to_update.pdf_url = file_url
            file_name = "{name}".format
            backfill_to_update.file_name = file_name(name=receipt)
            backfill_to_update.save()
        return Response(BackfillSerializer(backfill_to_update).data, status=status.HTTP_200_OK)


class ActiveBackfillRequest(APIView):
    permission_classes = [IsAuthenticated]

    def get_backfill(self, loan_pk):
        return get_or_not_found(Backfill, loan__id=loan_pk, loan__cart__status='active', status='backfill_active')

    def get(self, request, pk, format=None):
        active_backfill = self.get_backfill(pk)
        return Response(BackfillSerializer(active_backfill).data, status=status.HTTP_200_OK)


class ApproveBackfillRequest(APIView):
    permission_classes = [IsStaffUser]

    def patch(self, request, pk, format=None):
        backfill_request_to_approve = get_or_not_found(Backfill, pk=pk)
        if backfill_request_to_approve.status != 'backfill_request':
            raise MethodNotAllowed(self.patch, detail="Cannot approve backfill because it is not in the backfill request "
                                                      "state")
        cart = backfill_request_to_approve.loan.cart
        #to prevent them from calling this api for a request that is outstanding
        if cart.status == 'outstanding':
            raise MethodNotAllowed(self.patch, detail="Please approve the entire request if you would like to approve"
                                                      " this backfill request")
        #get the backfills that are approved or satisified associated with this loan
        #cannot approve this backfill if total quantity of those approved or satisfied is greater than overall loan quantity
        #e.g. request backfill of 4, then another of 4. both would be in backfill_request state, but annot approve both
        # since would be approving total of 8 when only have 7 loaned out
        approved_quantity = 0
        approved_backfill_requests = backfill_request_to_approve.loan.backfill_loan.filter(status='backfill_transit')
        for backfill in approved_backfill_requests:
            approved_quantity = approved_quantity + backfill.quantity
        potential_approved_quantity = approved_quantity + backfill_request_to_approve.quantity
        if potential_approved_quantity > backfill_request_to_approve.loan.quantity:
            raise MethodNotAllowed(self.patch, detail="Cannot approve this backfill because approving this backfill "
                                                      "would lead to approved quantity exceeding loaned quantity")
        backfill_request_to_approve.status = 'backfill_transit'
        backfill_request_to_approve.timestamp = datetime.now()
        backfill_request_to_approve.save()
        comment_str = "Backfill for quantity {quantity} was approved for loaned {item_name}, " \
                      "which is part of request with status {status}".format
        comment = comment_str(quantity=backfill_request_to_approve.quantity,
                              item_name=backfill_request_to_approve.loan.item.name, status=cart.status)
        LoggerUtility.log(initiating_user=request.user, nature_enum=ActionEnum.BACKFILL_APPROVED,
                          affected_user=backfill_request_to_approve.loan.cart.owner,
                          items_affected=[backfill_request_to_approve.loan.item], comment=comment,
                          carts_affected=[backfill_request_to_approve.loan.cart])
        EmailUtility.email(recipient=cart.owner.email, template='backfill_create_approve_deny_cancel',
                           context={'name': cart.owner.username,
                                    'backfill_state': 'approved',
                                    'item_name': backfill_request_to_approve.loan.item.name,
                                    'quantity': backfill_request_to_approve.quantity},
                           subject="Backfill Request Approved")
        return Response(BackfillSerializer(backfill_request_to_approve).data, status=status.HTTP_200_OK)


class DenyBackfillRequest(APIView):
    permission_classes = [IsStaffUser]

    def patch(self, request, pk, format=None):
        backfill_request_to_deny = get_or_not_found(Backfill, pk=pk)
        if backfill_request_to_deny.status != 'backfill_request':
            raise MethodNotAllowed(self.patch, detail="Cannot deny backfill because it is not in the backfill request "
                                                      "state")
        cart = backfill_request_to_deny.loan.cart
        if cart.status == 'outstanding':
            raise MethodNotAllowed(self.patch, detail="Please deny the entire request if you would like to deny"
                                                      " this backfill request")
        backfill_request_to_deny.status='backfill_denied'
        backfill_request_to_deny.timestamp = datetime.now()
        backfill_request_to_deny.save()
        associated_loan = backfill_request_to_deny.loan
        if associated_loan.returned_timestamp:
            associated_loan.returned_timestamp = None
            associated_loan.save()
        comment_str = "Backfill for quantity {quantity} was denied for loaned {item_name}, " \
                      "which is part of request with status {status}".format
        comment = comment_str(quantity=backfill_request_to_deny.quantity,
                              item_name=backfill_request_to_deny.loan.item.name, status=cart.status)
        LoggerUtility.log(initiating_user=request.user, nature_enum=ActionEnum.BACKFILL_DENIED,
                          affected_user=backfill_request_to_deny.loan.cart.owner,
                          items_affected=[backfill_request_to_deny.loan.item], comment=comment,
                          carts_affected=[backfill_request_to_deny.loan.cart])
        EmailUtility.email(recipient=cart.owner.email, template='backfill_create_approve_deny_cancel',
                           context={'name': cart.owner.username,
                                    'backfill_state': 'denied',
                                    'item_name': backfill_request_to_deny.loan.item.name,
                                    'quantity': backfill_request_to_deny.quantity},
                           subject="Backfill Request Denied")
        return Response(BackfillSerializer(backfill_request_to_deny).data, status=status.HTTP_200_OK)


class FailBackfillRequest(APIView):
    permission_classes = [IsStaffUser]

    def patch(self, request, pk, format=None):
        backfill_request_to_fail = get_or_not_found(Backfill, pk=pk)
        if backfill_request_to_fail.status != 'backfill_transit':
            raise MethodNotAllowed(self.patch, detail="Cannot mark a backfill as failed if it hasn't been approved "
                                                      "first and is not in transit")
        associated_cart = backfill_request_to_fail.loan.cart
        backfill_request_to_fail.status = 'backfill_failed'
        backfill_request_to_fail.timestamp = datetime.now()
        backfill_request_to_fail.save()
        associated_loan = backfill_request_to_fail.loan
        if associated_loan.returned_timestamp:
            associated_loan.returned_timestamp = None
            associated_loan.save()
        comment_str = "Backfill for quantity {quantity} was marked failed for loaned {item_name}, " \
                      "which is part of request with status {status}".format
        comment = comment_str(quantity=backfill_request_to_fail.quantity,
                              item_name=backfill_request_to_fail.loan.item.name,
                              status=backfill_request_to_fail.loan.cart.status)
        LoggerUtility.log(initiating_user=request.user, nature_enum=ActionEnum.BACKFILL_FAILED,
                          affected_user=backfill_request_to_fail.loan.cart.owner,
                          items_affected=[backfill_request_to_fail.loan.item], comment=comment,
                          carts_affected=[backfill_request_to_fail.loan.cart])
        EmailUtility.email(recipient=associated_cart.owner.email, template='backfill_satisfy_fail',
                           context={'name': associated_cart.owner.username,
                                    'backfill_state': 'failed',
                                    'item_name': backfill_request_to_fail.loan.item.name,
                                    'quantity': backfill_request_to_fail.quantity},
                           subject="Failed Backfill Request")
        return Response(BackfillSerializer(backfill_request_to_fail).data, status=status.HTTP_200_OK)


def validate_assets(data, backfill_request_to_satisfy, item):
    if item.is_asset:
        if data.get('asset_ids'):
            json_asset_ids = data.get('asset_ids')
            if not isinstance(json_asset_ids, list):
                raise ParseError(detail='Asset ids must be in list, it is in {type}'.format(type=type(json_asset_ids)))
            assets = item.assets.filter(pk__in=[id.get('asset_id') for id in json_asset_ids],
                                        loan=backfill_request_to_satisfy.loan)
            if not (backfill_request_to_satisfy.quantity == assets.count()):
                raise MethodNotAllowed(method=validate_assets, detail='Please specify  the same number'
                                                                      ' of assets that were requested')
            return assets
        raise ParseError(detail='Since item is an asset, Specify asset ids')
    return []


def add_asset_to_disbursement(disbursement, assets):
    for asset in assets:
        asset.disbursement = disbursement
        asset.loan = None
        asset.save()

# reduce quantity that is loaned out - convert to disbursement, add to available quantity


class SatisfyBackfillRequest(APIView):
    permission_classes = [IsStaffUser]

    def patch(self, request, pk, format=None):
        backfill_request_to_satisfy = get_or_not_found(Backfill, pk=pk)
        if backfill_request_to_satisfy.status != 'backfill_transit':
            raise MethodNotAllowed(self.patch, detail="Cannot mark a backfill as satisfied if it hasn't been approved "
                                                      "first and is not in transit")
        # if backfill request quantity = loaned quantity, then have to get rid of loan and add it as a disbursement
        associated_loan = backfill_request_to_satisfy.loan
        associated_cart = associated_loan.cart
        associated_item = associated_loan.item
        assets = validate_assets(request.data, backfill_request_to_satisfy, associated_item)
        backfill_request_to_satisfy.status = 'backfill_satisfied'
        backfill_request_to_satisfy.save()
        if backfill_request_to_satisfy.quantity == backfill_request_to_satisfy.loan.quantity:
            associated_loan.delete()
        else:
            associated_loan.quantity = associated_loan.quantity - backfill_request_to_satisfy.quantity
            associated_loan.save()
        if associated_cart.cart_disbursements.filter(item=associated_loan.item).exists():
            disbursement = associated_cart.cart_disbursements.get(item=associated_loan.item)
            disbursement.quantity = disbursement.quantity + backfill_request_to_satisfy.quantity
            disbursement.from_backfill = True
            disbursement.save()
        else:
            disbursement = Disbursement.objects.create(cart=backfill_request_to_satisfy.loan.cart, item=associated_item,
                                                       quantity=backfill_request_to_satisfy.quantity,
                                                       from_backfill=True)
        # add quantity back to available quantity
        add_asset_to_disbursement(disbursement, assets)
        associated_item.quantity = associated_item.quantity + backfill_request_to_satisfy.quantity
        associated_item.save()
        if associated_item.is_asset:
            [create_asset_helper(item=associated_item) for x in range(backfill_request_to_satisfy.quantity)]
        comment_str = "Backfill for quantity {quantity} was marked satisfied for loaned {item_name}, " \
                      "which is part of request with status {status}".format
        comment = comment_str(quantity=backfill_request_to_satisfy.quantity, item_name=associated_loan.item.name,
                              status=associated_cart.status)
        LoggerUtility.log(initiating_user=request.user, nature_enum=ActionEnum.BACKFILL_SATISFIED,
                          affected_user=associated_cart.owner,
                          items_affected=[associated_item], comment=comment, carts_affected=[associated_cart])
        EmailUtility.email(recipient=associated_cart.owner.email, template='backfill_satisfy_fail',
                           context={'name': associated_cart.owner.username,
                                    'backfill_state': 'satisfied',
                                    'item_name': associated_item.name,
                                    'quantity': backfill_request_to_satisfy.quantity},
                           subject="Satisfied Backfill Request")
        return Response(BackfillSerializer(backfill_request_to_satisfy).data, status=status.HTTP_200_OK)
