from rest_framework import filters
from rest_framework import generics
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from inventoryProject.permissions import IsStaffOrReadOnly, IsSuperUserDelete, IsStaffUser
from inventory_transaction_logger.action_enum import ActionEnum
from inventory_transaction_logger.utility.logger import LoggerUtility
from items.custom_pagination import LargeResultsSetPagination
from items.logic.filter_item_logic import FilterItemLogic
from items.models import Item
from items.serializers.detailed_item_serializer import DetailedItemSerializer
from items.serializers.item_serializer import ItemSerializer, UniqueItemSerializer, ItemQuantitySerializer


class ItemList(generics.ListCreateAPIView):
    permission_classes = [IsStaffOrReadOnly]
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
    permission_classes = [IsStaffOrReadOnly, IsSuperUserDelete]
    queryset = Item.objects.all()
    serializer_class = DetailedItemSerializer

    def delete(self, request, *args, **kwargs):
        item_name = self.get_object().name
        return_value = self.destroy(request, *args, **kwargs)
        #LoggerUtility.log_as_system(ActionEnum.ITEM_DESTROYED, request.user.username + " DESTROYED " + item_name)
        comment_string = "Item with name {name} was deleted by {username}".format
        comment = comment_string(name=item_name, username=request.user.username)
        LoggerUtility.log(initiating_user=request.user, nature_enum=ActionEnum.ITEM_DELETED, comment=comment, items_affected=[self.get_object()])
        return return_value

    def patch(self, request, *args, **kwargs):
        if request.user.is_staff and not request.user.is_superuser and request.data.get('quantity') is not None:
            raise PermissionDenied('Staff/Managers are not allowed to change the quantity')
        return self.partial_update(request, *args, **kwargs)


class UniqueItemList(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Item.objects.all().values('id', 'name').distinct()
    serializer_class = UniqueItemSerializer
    pagination_class = LargeResultsSetPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name', )


class ItemQuantityModification(generics.CreateAPIView):
    permission_classes = [IsStaffUser]
    serializer_class = ItemQuantitySerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        item = serializer.save()
        item_serializer = ItemSerializer(item)
        return Response(item_serializer.data, status=status.HTTP_200_OK)


