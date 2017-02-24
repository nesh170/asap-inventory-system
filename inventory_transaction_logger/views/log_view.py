from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from inventory_transaction_logger.models import Log
from inventory_transaction_logger.serializers.log_serializer import LogSerializer


class LogList(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Log.objects.all()
    serializer_class = LogSerializer
    #filter_backends = (DjangoFilterBackend, )
    #filter_fields = ('user', 'timestamp', 'action__tag')




def get_log(pk):
    try:
        return Log.objects.get(pk=pk)
    except Log.DoesNotExist:
        raise NotFound(detail="Log not found")

class ViewDetailedLog(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, pk, format=None):
        log = get_log(pk)
        serializer = LogSerializer(log)
        return Response(serializer.data)