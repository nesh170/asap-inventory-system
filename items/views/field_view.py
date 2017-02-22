from rest_framework import generics

from inventoryProject.permissions import IsSuperUser, IsStaffUser
from items.models import Field, IntField, FloatField, ShortTextField, LongTextField
from items.serializers.field_serializer import FieldSerializer, IntFieldSerializer, FloatFieldSerializer, \
    ShortTextFieldSerializer, LongTextFieldSerializer


class FieldList(generics.ListCreateAPIView):
    queryset = Field.objects.all()
    permission_classes = [IsSuperUser]
    serializer_class = FieldSerializer


class FieldDeletion(generics.DestroyAPIView):
    queryset = Field.objects.all()
    permission_classes = [IsSuperUser]
    serializer_class = FieldSerializer


class IntFieldUpdate(generics.UpdateAPIView):
    queryset = IntField.objects.all()
    permission_classes = [IsStaffUser]
    serializer_class = IntFieldSerializer


class FloatFieldUpdate(generics.UpdateAPIView):
    queryset = FloatField.objects.all()
    permission_classes = [IsStaffUser]
    serializer_class = FloatFieldSerializer


class ShortTextFieldUpdate(generics.UpdateAPIView):
    queryset = ShortTextField.objects.all()
    permission_classes = [IsStaffUser]
    serializer_class = ShortTextFieldSerializer


class LongTextFieldUpdate(generics.UpdateAPIView):
    queryset = LongTextField.objects.all()
    permission_classes = [IsStaffUser]
    serializer_class = LongTextFieldSerializer


