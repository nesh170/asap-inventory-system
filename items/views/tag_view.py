from rest_framework import filters
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from inventoryProject.permissions import IsStaffUser
from inventoryProject.utility.print_functions import serializer_pretty_print
from inventory_transaction_logger.action_enum import ActionEnum
from inventory_transaction_logger.utility.logger import LoggerUtility
from items.custom_pagination import LargeResultsSetPagination
from items.models import Tag
from items.serializers.tag_serializer import TagSerializer, TagSingleSerializer


class TagList(generics.CreateAPIView):
    queryset = Tag.objects.all()
    permission_classes = [IsStaffUser]
    serializer_class = TagSerializer

    def perform_create(self, serializer):
        serializer.save()
        item= serializer.instance.item
        comment = serializer_pretty_print(serializer=serializer, title=ActionEnum.TAG_CREATED.value) + \
            "Item name: {item}\n".format(item=item.name)
        LoggerUtility.log(initiating_user=self.request.user, nature_enum=ActionEnum.TAG_CREATED, comment=comment,
                          items_affected=[item])


class TagDeletion(generics.DestroyAPIView):
    permission_classes = [IsStaffUser]
    queryset = Tag.objects.all()

    def perform_destroy(self, instance):
        tag = self.get_object()
        item = tag.item
        serializer = TagSerializer(tag)
        comment = serializer_pretty_print(serializer=serializer, title=ActionEnum.TAG_DELETED.value,
                                          validated=False) + "Item name: {item}\n".format(item=item.name)
        LoggerUtility.log(initiating_user=self.request.user, nature_enum=ActionEnum.TAG_DELETED, comment=comment,
                          items_affected=[item])
        instance.delete()


class UniqueTagList(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Tag.objects.all().values('tag').distinct()
    serializer_class = TagSingleSerializer
    pagination_class = LargeResultsSetPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('tag', )