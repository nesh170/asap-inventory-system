from rest_framework import filters
from rest_framework import generics

from inventoryProject.permissions import IsAdminOrReadOnly
from inventory_logger.action_enum import ActionEnum
from inventory_logger.utility.logger import LoggerUtility
from items.custom_pagination import LargeResultsSetPagination
from items.logic.filter_item_logic import FilterItemLogic
from items.models import Item
from items.serializers.detailed_item_serializer import DetailedItemSerializer
from items.serializers.item_serializer import ItemSerializer, UniqueItemSerializer


class ItemList(generics.ListCreateAPIView):
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = ItemSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name', 'model_number', 'tags__tag')

    def get_queryset(self):
        filter_item_logic = FilterItemLogic()
        if self.request.method == 'GET':
            tag_included = self.request.GET.get('tag_included')
            tag_excluded = self.request.GET.get('tag_excluded')
            operation = self.request.GET.get('operator')
            if tag_included is not None or tag_excluded is not None:
                return filter_item_logic.filter_logic(tag_included, tag_excluded, operation)
        return Item.objects.all()


class ItemDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminOrReadOnly]
    queryset = Item.objects.all()
    serializer_class = DetailedItemSerializer

    def delete(self, request, *args, **kwargs):
        item_name = self.get_object().name
        return_value = self.destroy(request, *args, **kwargs)
        LoggerUtility.log_as_system(ActionEnum.ITEM_DESTROYED, request.user.username + " DESTROYED " + item_name)
        return return_value


class UniqueItemList(generics.ListAPIView):
    permission_classes = [IsAdminOrReadOnly]
    queryset = Item.objects.all().values('id', 'name').distinct()
    serializer_class = UniqueItemSerializer
    pagination_class = LargeResultsSetPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name', )

