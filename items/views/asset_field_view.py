from rest_framework import generics
from rest_framework.exceptions import ParseError

from inventoryProject.permissions import IsSuperUserOrStaffReadOnly, IsSuperUser, IsStaffUser
from items.models.asset_custom_fields import AssetField, IntAssetField, FloatAssetField, ShortTextAssetField, \
    LongTextAssetField
from items.serializers.asset_field_serializer import AssetFieldSerializer, IntAssetFieldSerializer, \
    FloatAssetFieldSerializer, ShortTextAssetFieldSerializer, LongTextAssetFieldSerializer


class AssetFieldList(generics.ListCreateAPIView):
    queryset = AssetField.objects.all()
    permission_classes = [IsSuperUserOrStaffReadOnly]
    serializer_class = AssetFieldSerializer


class AssetFieldDetailed(generics.RetrieveUpdateDestroyAPIView):
    queryset = AssetField.objects.all()
    permission_classes = [IsSuperUser]
    serializer_class = AssetFieldSerializer

    def perform_update(self, serializer):
        if serializer.validated_data.get('type') is not None:
            raise ParseError(detail='You cannot change the type of a field')
        serializer.save()


class IntAssetFieldUpdate(generics.UpdateAPIView):
    queryset = IntAssetField.objects.all()
    permission_classes = [IsStaffUser]
    serializer_class = IntAssetFieldSerializer


class FloatAssetFieldUpdate(generics.UpdateAPIView):
    queryset = FloatAssetField.objects.all()
    permission_classes = [IsStaffUser]
    serializer_class = FloatAssetFieldSerializer


class ShortTextAssetFieldUpdate(generics.UpdateAPIView):
    queryset = ShortTextAssetField.objects.all()
    permission_classes = [IsStaffUser]
    serializer_class = ShortTextAssetFieldSerializer


class LongTextAssetFieldUpdate(generics.UpdateAPIView):
    queryset = LongTextAssetField.objects.all()
    permission_classes = [IsStaffUser]
    serializer_class = LongTextAssetFieldSerializer

