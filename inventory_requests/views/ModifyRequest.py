# Create your views here.
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

def get_object(pk):
    try:
        return Request.objects.get(pk=pk)
    except Request.DoesNotExist:
        raise Http404
class ApproveRequest(APIView):
   permission_classes = [TokenHasReadWriteScope, IsAdminUser]
   def patch(self, request, pk, format=None):
       request_to_approve = get_object(pk)
       if modify_request_logic.can_approve_deny_cancel_request(request_to_approve):
           request_to_approve.status = "approved"
           serializer = StatusSerializer.StatusSerializer(request_to_approve, data=request.data)
           if serializer.is_valid():
               LoggerUtility.log_as_system(ActionEnum.REQUEST_APPROVED, "Request (ID: " + request_to_approve.id + ") Approved")
               serializer.save(admin=request.user, admin_timestamp=datetime.now(), admin_comment=request.data.get('admin_comment'))
               modify_request_logic.approve_request(request_to_approve)

               return Response(serializer.data)
           return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
       else:
           raise MethodNotAllowed(self.patch, "Cannot approve request")

class CancelRequest(APIView):
    permission_classes = [TokenHasReadWriteScope, IsAuthenticated]
    def patch(self, request, pk, format=None):
        request_to_cancel = get_object(pk)
        if modify_request_logic.can_approve_deny_cancel_request(request_to_cancel):
            request_to_cancel.status = "cancelled"
            request.data['reason'] = request_to_cancel.reason + " cancellation reason is : " + request.data.get('reason')
            serializer = CancelSerializer.CancelSerializer(request_to_cancel, data=request.data)
            if serializer.is_valid():
                LoggerUtility.log_as_system(ActionEnum.REQUEST_CANCELLED, "Request (ID: " + request_to_cancel.id + ") Cancelled")
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            raise MethodNotAllowed(self.patch, "Cannot cancel request")


class DenyRequest(APIView):
    permission_classes = [TokenHasReadWriteScope, IsAdminUser]
    def patch(self, request, pk, format=None):
        request_to_deny = get_object(pk)
        if modify_request_logic.can_approve_deny_cancel_request(request_to_deny):
            request_to_deny.status = "denied"
            request.data['admin_comment'] = request_to_deny.admin_comment + " denial reason is : " + request.data.get('admin_comment')
            serializer = StatusSerializer.StatusSerializer(request_to_deny, data=request.data)
            if serializer.is_valid():
                LoggerUtility.log_as_system(ActionEnum.REQUEST_DENIED, "Request (ID: " + request_to_deny.id + ") Denied")
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            raise MethodNotAllowed(self.patch, "Cannot deny request")