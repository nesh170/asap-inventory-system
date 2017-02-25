from rest_framework import generics

from inventoryProject.permissions import IsStaffOrReadOnly
from inventory_transaction_logger.models import Action
from inventory_transaction_logger.serializers.log_serializer import ActionSerializer
from items.custom_pagination import LargeResultsSetPagination


class ActionList(generics.ListCreateAPIView):
    permission_classes = [IsStaffOrReadOnly]
    queryset = Action.objects.all()
    serializer_class = ActionSerializer
    pagination_class = LargeResultsSetPagination