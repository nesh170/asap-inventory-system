

from inventory_requests.models import Request
from rest_framework import filters
from rest_framework.response import Response
from rest_framework.views import APIView

from inventory_requests.serializers import RequestSerializer

class RequestList(APIView):
    def get(self, request, format=None):
        requestsQuerySet = Request.objects.all()
        serializer = RequestSerializer.RequestSerializer(requestsQuerySet, many=True)
        filter_backends = (filters.SearchFilter, filters.DjangoFilterBackend)
        filter_fields = ('owner__username', 'item__name', 'status', 'quantity')
        search_fields = ('owner__username', 'item__name', 'reason')
        return Response(serializer.data)