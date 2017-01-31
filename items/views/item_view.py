from rest_framework import generics
from rest_framework.decorators import permission_classes
from rest_framework import filters
from inventoryProject.permissions import IsAdminOrReadOnly
from items.models import Item
from items.serializers.item_serializer import ItemSerializer
from oauth2_provider.ext.rest_framework import TokenHasReadWriteScope, TokenHasScope


@permission_classes((IsAdminOrReadOnly,))
class ItemList(generics.ListCreateAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name', 'model_number', 'tags__tag')


@permission_classes((IsAdminOrReadOnly,))
class ItemDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
