from django.http import Http404
from inventory_requests.models import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from inventory_requests.serializers import RequestSerializer

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