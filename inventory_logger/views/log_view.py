from rest_framework import generics
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAdminUser
from inventory_logger.models import Log
from inventory_logger.serializers.log_serializer import LogSerializer
from django_filters.rest_framework import DjangoFilterBackend


@permission_classes((IsAdminUser,))
class LogList(generics.ListAPIView):
    queryset = Log.objects.all()
    serializer_class = LogSerializer
    filter_backends = (DjangoFilterBackend, )
    filter_fields = ('user', 'action', 'timestamp')


