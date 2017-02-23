from oauth2_provider.ext.rest_framework import TokenHasReadWriteScope
from rest_framework import generics

from inventoryProject.permissions import IsStaffOrReadOnly
from inventory_logger.models import Action
from inventory_logger.serializers.log_serializer import ActionSerializer


class ActionList(generics.ListCreateAPIView):
    permission_classes = [IsStaffOrReadOnly]
    queryset = Action.objects.all()
    serializer_class = ActionSerializer
    paginate_by = None
    paginate_by_param = None
