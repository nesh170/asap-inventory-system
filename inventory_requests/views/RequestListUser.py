from inventory_requests.models import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from inventory_requests.serializers import RequestSerializer

class RequestListUser(APIView):
    def get(self, request, format=None):
       requestsQuerySet = Request.objects.filter(owner=request.user)
       serializer = RequestSerializer.RequestSerializer(requestsQuerySet, many=True)
       return Response(serializer.data)