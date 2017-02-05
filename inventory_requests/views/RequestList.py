from rest_framework import generics

from inventory_requests.models import Request
from inventory_requests.serializers.RequestSerializer import RequestSerializer


class RequestList(generics.ListCreateAPIView):
    queryset = Request.objects.all()
    serializer_class = RequestSerializer


# class RequestList(APIView):
    # def get(self, request, format=None):
    #     requestsQuerySet = Request.objects.all()
    #     serializer = RequestSerializer.RequestSerializer(requestsQuerySet, many=True)
    #     filter_backends = (filters.SearchFilter, filters.DjangoFilterBackend)
    #     filter_fields = ('owner__username', 'item__name', 'status', 'quantity')
    #     search_fields = ('owner__username', 'item__name', 'reason')
    #     return Response(serializer.data)
#used for get all requests and create request


