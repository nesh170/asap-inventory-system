from rest_framework import filters
from oauth2_provider.ext.rest_framework import TokenHasReadWriteScope
from rest_framework import generics
from items.custom_pagination import LargeResultsSetPagination

from inventoryProject.permissions import IsAdminOrReadOnly
from items.models import Tag
from items.serializers.tag_serializer import TagSerializer


class TagList(generics.ListCreateAPIView):
    queryset = Tag.objects.all()
    permission_classes = [IsAdminOrReadOnly, TokenHasReadWriteScope]
    serializer_class = TagSerializer
    pagination_class = LargeResultsSetPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('tag', )


class TagDeletion(generics.DestroyAPIView):
    permission_classes = [IsAdminOrReadOnly, TokenHasReadWriteScope]
    queryset = Tag.objects.all()




