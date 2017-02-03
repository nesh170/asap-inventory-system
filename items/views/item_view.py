from oauth2_provider.ext.rest_framework import TokenHasReadWriteScope
from rest_framework import filters
from rest_framework import generics

from inventoryProject.permissions import IsAdminOrReadOnly
from inventory_logger.action_enum import ActionEnum
from inventory_logger.utility.logger import LoggerUtility
from items.models import Item
from items.serializers.item_serializer import ItemSerializer


class ItemList(generics.ListCreateAPIView):
    permission_classes = [IsAdminOrReadOnly]
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name', 'model_number', 'tags__tag')


class ItemDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminOrReadOnly, TokenHasReadWriteScope]
    queryset = Item.objects.all()
    serializer_class = ItemSerializer

    def delete(self, request, *args, **kwargs):
        item_name = self.get_object().name
        return_value = self.destroy(request, *args, **kwargs)
        LoggerUtility.log_as_system(ActionEnum.ITEM_DESTROYED, request.user.username + " DESTROYED " + item_name)
        return return_value
