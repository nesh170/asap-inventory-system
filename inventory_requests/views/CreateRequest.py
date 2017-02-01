from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from inventory_requests.serializers import RequestSerializer

# this create class has to be fixed
class CreateRequest(APIView):
    def post(self, request, format=None):
        serializer = RequestSerializer.RequestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(owner=request.user)  # creates a new instance
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)