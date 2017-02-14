from oauth2_provider.ext.rest_framework import TokenHasReadWriteScope
from rest_framework import generics
from rest_framework.permissions import IsAdminUser

from items.models import Field
from items.serializers.field_serializer import FieldSerializer


class FieldList(generics.ListCreateAPIView):
    queryset = Field.objects.all()
    permission_classes = [IsAdminUser, TokenHasReadWriteScope]
    serializer_class = FieldSerializer


class FieldDeletion(generics.DestroyAPIView):
    queryset = Field.objects.all()
    permission_classes = [IsAdminUser, TokenHasReadWriteScope]
    serializer_class = FieldSerializer


