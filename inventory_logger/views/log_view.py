from django_filters.rest_framework import DjangoFilterBackend
from oauth2_provider.ext.rest_framework import TokenHasReadWriteScope
from rest_framework import generics

from inventoryProject.permissions import IsAdminOrReadOnly
from inventory_logger.models import Log
from inventory_logger.serializers.log_serializer import LogSerializer


class LogList(generics.ListCreateAPIView):
    permission_classes = [IsAdminOrReadOnly, TokenHasReadWriteScope]
    queryset = Log.objects.all()
    serializer_class = LogSerializer
    filter_backends = (DjangoFilterBackend, )
    filter_fields = ('user', 'timestamp', 'action__tag')


