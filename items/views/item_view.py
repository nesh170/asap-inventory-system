from django.db.models import F
from rest_framework import filters
from rest_framework import generics
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from inventoryProject.permissions import IsStaffOrReadOnly, IsSuperUserDelete, IsStaffUser
from inventoryProject.utility.print_functions import serializer_pretty_print, serializer_compare_pretty_print
from inventory_transaction_logger.action_enum import ActionEnum
from inventory_transaction_logger.utility.logger import LoggerUtility
from items.custom_pagination import LargeResultsSetPagination
from items.logic.filter_item_logic import FilterItemLogic
from items.models.item_models import Item
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
            threshold = self.request.GET.get('threshold')
            current_queryset = Item.objects.all()
            if tag_included is not None or tag_excluded is not None:
                current_queryset = filter_item_logic.filter_tag_logic(tag_included, tag_excluded, operation)
            if threshold is not None and threshold.lower() == 'true':
                current_queryset = current_queryset.filter(minimum_stock__gt=F('quantity'))
        return current_queryset

    def perform_create(self, serializer):
        serializer.save()
        comment = serializer_pretty_print(serializer=serializer, title=ActionEnum.ITEM_CREATED.value)
        LoggerUtility.log(initiating_user=self.request.user, nature_enum=ActionEnum.ITEM_CREATED,
                          comment=comment, items_affected=[serializer.instance])


class ItemDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsStaffOrReadOnly, IsSuperUserDelete]
    queryset = Item.objects.all()
    serializer_class = DetailedItemSerializer

    def delete(self, request, *args, **kwargs):
        item = self.get_object()
        comment = serializer_pretty_print(serializer=ItemSerializer(item),
                                          title=ActionEnum.ITEM_DELETED.value, validated=False)
        LoggerUtility.log(initiating_user=request.user, nature_enum=ActionEnum.ITEM_DELETED, comment=comment,
                          items_affected=[item])
        return_value = self.destroy(request, *args, **kwargs)
        return return_value

    def perform_update(self, serializer):
        old_serializer = ItemSerializer(self.get_object())
        serializer.save()
        updated_item = self.get_object()
        updated_serializer = ItemSerializer(updated_item)
        comment = serializer_compare_pretty_print(old_serializer=old_serializer, new_serializer=updated_serializer,
                                                  validated=False, title=ActionEnum.ITEM_MODIFIED.value)
        LoggerUtility.log(initiating_user=self.request.user, nature_enum=ActionEnum.ITEM_MODIFIED,
                          comment=comment, items_affected=[updated_item])

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