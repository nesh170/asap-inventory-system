from inventory_requests.models import Request
from rest_framework import filters
from rest_framework.response import Response
from rest_framework.views import APIView

from inventory_requests.serializers import RequestSerializer

class RequestList(APIView):
    def get(self, request, format=None):
        print("getting all requests")
        requestsQuerySet = Request.objects.all()
        serializer = RequestSerializer.RequestSerializer(requestsQuerySet, many=True)
        filter_backends = (filters.SearchFilter,)
        search_fields = ('owner', 'status', 'item', 'quantity', 'reason', 'timestamp', 'admin_timestamp', 'system_comment', 'admin_comment', 'admin')
        return Response(serializer.data)