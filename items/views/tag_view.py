from rest_framework import filters
from rest_framework import generics

from inventoryProject.permissions import IsAdminOrReadOnly
from items.custom_pagination import LargeResultsSetPagination
from items.models import Tag
from items.serializers.tag_serializer import TagSerializer, TagSingleSerializer


class TagList(generics.CreateAPIView):
    queryset = Tag.objects.all()
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = TagSerializer


class TagDeletion(generics.DestroyAPIView):
    permission_classes = [IsAdminOrReadOnly]
    queryset = Tag.objects.all()


class UniqueTagList(generics.ListAPIView):
    permission_classes = [IsAdminOrReadOnly]
    queryset = Tag.objects.all().values('tag').distinct()
    serializer_class = TagSingleSerializer
    pagination_class = LargeResultsSetPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('tag', )




