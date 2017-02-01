from oauth2_provider.ext.rest_framework import TokenHasReadWriteScope
from rest_framework import filters
from rest_framework import generics

from inventoryProject.permissions import IsAdminOrReadOnly
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
