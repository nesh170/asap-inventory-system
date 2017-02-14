from django.http import Http404
from oauth2_provider.ext.rest_framework import TokenHasReadWriteScope
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from inventory_requests.models import Request
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from inventory_requests.business_logic import modify_request_logic
from inventory_requests.serializers import StatusSerializer, CancelSerializer
from datetime import datetime
from inventory_logger.utility.logger import LoggerUtility
from inventory_logger.action_enum import ActionEnum


def approveDenyRequest(self, request, pk, request_type):
    request_to_approve_deny = get_object(pk)
    if (request_type == "approved"):
        type_for_comment = "approval"
        log_action = ActionEnum.REQUEST_APPROVED
    else:
        type_for_comment = "denial"
        log_action = ActionEnum.REQUEST_DENIED
    if modify_request_logic.can_approve_deny_cancel_request(request_to_approve_deny, request_type):
        request_to_approve_deny.status = request_type
        if (request_to_approve_deny.admin_comment is not None):
            if (request.data.get('admin_comment') is not None):
                request.data[
                    'admin_comment'] = request_to_approve_deny.admin_comment + " " + type_for_comment + " reason is : " + request.data.get(
                    'admin_comment')
            else:
                request.data['admin_comment'] = request_to_approve_deny.admin_comment;
        else:
            if (request.data.get('admin_comment') is not None):
                request.data['admin_comment'] = type_for_comment + " reason is : " + request.data.get('admin_comment')
            else:
                request.data['admin_comment'] = None;
        serializer = StatusSerializer.StatusSerializer(request_to_approve_deny, data=request.data)
        if serializer.is_valid():
            LoggerUtility.log_as_system(log_action,
                                        "Request (ID: " + str(request_to_approve_deny.id) + ") " + request_type)
            serializer.save(admin=request.user, admin_timestamp=datetime.now())
            if request_type == "approved":
                modify_request_logic.approve_request(request_to_approve_deny)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        raise MethodNotAllowed(self.patch, "Request cannot be " + request_type)


def get_object(pk):
    try:
        return Request.objects.get(pk=pk)
    except Request.DoesNotExist:
        raise Http404
class ApproveRequest(APIView):
   permission_classes = [TokenHasReadWriteScope, IsAdminUser]
   def patch(self, request, pk, format=None):
       return approveDenyRequest(self, request, pk, "approved")

class CancelRequest(APIView):
    permission_classes = [TokenHasReadWriteScope, IsAuthenticated]
    def patch(self, request, pk, format=None):
        request_to_cancel = get_object(pk)
        if modify_request_logic.can_approve_deny_cancel_request(request_to_cancel, "cancelled"):
            request_to_cancel.status = "cancelled"
            #reason is guaranteed to not be null since it is required in a request
            if (request.data.get('reason') is not None):
                request.data['reason'] = request_to_cancel.reason + " cancellation reason is : " + request.data.get('reason')
            else:
                request.data['reason'] = request_to_cancel.reason;
            serializer = CancelSerializer.CancelSerializer(request_to_cancel, data=request.data)
            if serializer.is_valid():
                LoggerUtility.log_as_system(ActionEnum.REQUEST_CANCELLED, "Request (ID: " + str(request_to_cancel.id) + ") Cancelled")
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            raise MethodNotAllowed(self.patch, "Cannot cancel request")


class DenyRequest(APIView):
    permission_classes = [TokenHasReadWriteScope, IsAdminUser]
    def patch(self, request, pk, format=None):
        return approveDenyRequest(self, request, pk, "denied")