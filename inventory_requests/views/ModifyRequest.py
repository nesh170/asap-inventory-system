# Create your views here.
from django.http import Http404
from rest_framework.exceptions import MethodNotAllowed

from inventory_requests.models import Request
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from inventory_requests.business_logic import modify_request_logic
from inventory_requests.serializers import RequestSerializer
from inventory_requests.serializers import StatusSerializer, CancelSerializer
from datetime import datetime

def get_object(pk):
    try:
        return Request.objects.get(pk=pk)
    except Request.DoesNotExist:
        raise Http404
class ApproveRequest(APIView):

   def patch(self, request, pk, format=None):
       print("running atch request")
       request_to_approve = get_object(pk)
       if modify_request_logic.can_approve_deny_cancel_request(request_to_approve):
           request_to_approve.status = "approved"
           serializer = StatusSerializer.StatusSerializer(request_to_approve, data=request.data)
           if serializer.is_valid():
               modify_request_logic.approve_request(request_to_approve)
               serializer.save(admin=request.user, admin_timestamp=datetime.now(), admin_comment=request.data.get('admin_comment'))
               return Response(serializer.data)
           return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
       else:
           raise MethodNotAllowed(self.patch, "Cannot approve request")

class CancelRequest(APIView):
    def patch(self, request, pk, format=None):
        request_to_cancel = get_object(pk)
        if modify_request_logic.can_approve_deny_cancel_request(request_to_cancel):
            request_to_cancel.status = "cancelled"
            request.data['reason'] = request_to_cancel.reason + " cancellation reason is : " + request.data.get('reason')
            serializer = CancelSerializer.CancelSerializer(request_to_cancel, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            raise MethodNotAllowed(self.patch, "Cannot cancel request")


class DenyRequest(APIView):
    def patch(self, request, pk, format=None):
        request_to_deny = get_object(pk)
        if modify_request_logic.can_approve_deny_cancel_request(request_to_deny):
            request_to_deny.status = "denied"
            request.data['admin_comment'] = request_to_deny.admin_comment + " denial reason is : " + request.data.get('admin_comment')
            serializer = StatusSerializer.StatusSerializer(request_to_deny, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            raise MethodNotAllowed(self.patch, "Cannot deny request")