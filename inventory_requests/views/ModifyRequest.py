# Create your views here.
from django.http import Http404
from inventory_requests.models import Request
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from inventory_requests.business_logic import modify_request_logic
from inventory_requests.serializers import RequestSerializer
class ModifyRequest(APIView):
   # FIX THIS CODE - IT IS CURRENTLY REPEATED BUT HAS TO BE REFACTORED SO IT IS NOT
   def get_object(self, pk):
       try:
           return Request.objects.get(pk=pk)
       except Request.DoesNotExist:
           raise Http404
   def patch(self, request, pk, format=None):
       print("running atch request")
       request_to_approve = self.get_object(pk)
       if modify_request_logic.can_approve_request(request_to_approve):
           modify_request_logic.approve_request(request_to_approve)
           serializer = RequestSerializer.RequestSerializer(request_to_approve, data=request.data)
           if serializer.is_valid():
               serializer.save()
               return Response(serializer.data)
           return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# Approve request based on a requestID