from rest_framework import filters
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from inventoryProject.permissions import IsStaffUser
from inventory_transaction_logger.action_enum import ActionEnum
from inventory_transaction_logger.utility.logger import LoggerUtility
from items.custom_pagination import LargeResultsSetPagination
from items.models import Tag, Item
from items.serializers.tag_serializer import TagSerializer, TagSingleSerializer


class TagList(generics.CreateAPIView):
    queryset = Tag.objects.all()
    permission_classes = [IsStaffUser]
    serializer_class = TagSerializer

    def perform_create(self, serializer):
        data = serializer.validated_data
        item = data.get('item')
        comment_string = "Tag with name {name} belonging to item with name {item_name} created".format
        comment = comment_string(name=data.get('tag'), item_name=item.name)
        LoggerUtility.log(initiating_user=self.request.user, nature_enum=ActionEnum.TAG_CREATED, comment=comment, items_affected=[item])
        serializer.save()

class TagDeletion(generics.DestroyAPIView):
    permission_classes = [IsStaffUser]
    queryset = Tag.objects.all()


    def perform_destroy(self, instance):
        item = self.get_object().item
        comment_string = "Tag with name {name} belonging to item with name {item_name} deleted".format
        comment = comment_string(name=instance.tag, item_name=item.name)
        LoggerUtility.log(initiating_user=self.request.user, nature_enum=ActionEnum.TAG_DELETED, comment=comment, items_affected=[item])
        instance.delete()

class UniqueTagList(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Tag.objects.all().values('tag').distinct()
    serializer_class = TagSingleSerializer
    pagination_class = LargeResultsSetPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('tag', )