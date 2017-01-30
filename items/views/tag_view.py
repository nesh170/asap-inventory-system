from rest_framework import generics
from rest_framework.decorators import permission_classes
from inventoryProject.permissions import IsAdminOrReadOnly
from items.models import Tag
from items.serializers.tag_serializer import TagSerializer


@permission_classes((IsAdminOrReadOnly,))
class TagCreation(generics.CreateAPIView):
    model = Tag
    serializer_class = TagSerializer


@permission_classes((IsAdminOrReadOnly,))
class TagDeletion(generics.DestroyAPIView):
    queryset = Tag.objects.all()


