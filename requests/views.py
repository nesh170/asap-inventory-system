from django.shortcuts import render

# Create your views here.
from requests.models import Request
from requests.serializers import RequestSerializer
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
class RequestList(APIView):
    def get(self, request, format=None):
        requestsQuerySet = Request.objects.all()
        serializer = RequestSerializer.RequestSerializer(requestsQuerySet, many=True)
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
#class RequestListUser(APIView):
    #def get(self, request, userID, format=None):
       # requestsQuerySet = Request.objects.
