# Create your views here.
from django.http import Http404
from inventory_requests.models import Request
from rest_framework import filters
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from inventory_requests.serializers import RequestSerializer


class RequestList(APIView):
    def get(self, request, format=None):
        requestsQuerySet = Request.objects.all()
        serializer = RequestSerializer.RequestSerializer(requestsQuerySet, many=True)
        filter_backends = (filters.SearchFilter,)
        search_fields = ('owner', 'status', 'item', 'quantity', 'reason', 'timestamp', 'admin_timestamp', 'system_comment', 'admin_comment', 'admin')
        return Response(serializer.data)
class ViewDetailedRequest(APIView):
    def get_object(self, pk):
        try:
            return Request.objects.get(pk=pk)
        except Request.DoesNotExist:
            raise Http404
    def get(self, request, pk, format=None):
        request = self.get_object(pk)
        serializer = RequestSerializer.RequestSerializer(request)
        return Response(serializer.data)
class RequestListUser(APIView):
    def get(self, request, format=None):
       requestsQuerySet = Request.objects.filter(owner=request.user)
       serializer = RequestSerializer.RequestSerializer(requestsQuerySet, many=True)
       return Response(serializer.data)
# this create class has to be fixed
class CreateRequest(APIView):
    def post(self, request, format=None):
        serializer = RequestSerializer.RequestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  # creates a new instance
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# Approve request based on a requestID
class ModifyRequest(APIView):
    # FIX THIS CODE - IT IS CURRENTLY REPEATED BUT HAS TO BE REFACTORED SO IT IS NOT
    def get_object(self, pk):
        try:
            return Request.objects.get(pk=pk)
        except Request.DoesNotExist:
            raise Http404
    def patch(self, request, pk, format=None):
        request_to_approve = self.get_object(pk)
        serializer = RequestSerializer.RequestSerializer(request_to_approve, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

