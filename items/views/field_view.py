from oauth2_provider.ext.rest_framework import TokenHasReadWriteScope
from rest_framework import generics
from rest_framework.permissions import IsAdminUser

from items.models import Field, IntField, FloatField, ShortTextField, LongTextField
from items.serializers.field_serializer import FieldSerializer, IntFieldSerializer, FloatFieldSerializer, \
    ShortTextFieldSerializer, LongTextFieldSerializer


class FieldList(generics.ListCreateAPIView):
    queryset = Field.objects.all()
    permission_classes = [IsAdminUser, TokenHasReadWriteScope]
    serializer_class = FieldSerializer


class FieldDeletion(generics.DestroyAPIView):
    queryset = Field.objects.all()
    permission_classes = [IsAdminUser, TokenHasReadWriteScope]
    serializer_class = FieldSerializer


class IntFieldUpdate(generics.UpdateAPIView):
    queryset = IntField.objects.all()
    permission_classes = [IsAdminUser, TokenHasReadWriteScope]
    serializer_class = IntFieldSerializer


class FloatFieldUpdate(generics.UpdateAPIView):
    queryset = FloatField.objects.all()
    permission_classes = [IsAdminUser, TokenHasReadWriteScope]
    serializer_class = FloatFieldSerializer


class ShortTextFieldUpdate(generics.UpdateAPIView):
    queryset = ShortTextField.objects.all()
    permission_classes = [IsAdminUser, TokenHasReadWriteScope]
    serializer_class = ShortTextFieldSerializer


class LongTextFieldUpdate(generics.UpdateAPIView):
    queryset = LongTextField.objects.all()
    permission_classes = [IsAdminUser, TokenHasReadWriteScope]
    serializer_class = LongTextFieldSerializer


