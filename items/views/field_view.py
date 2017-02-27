from rest_framework import generics

from inventoryProject.permissions import IsSuperUser, IsStaffUser
from inventoryProject.utility.print_functions import serializer_pretty_print, serializer_compare_pretty_print
from inventory_transaction_logger.utility.logger import LoggerUtility
from inventory_transaction_logger.action_enum import ActionEnum
from items.models import Field, IntField, FloatField, ShortTextField, LongTextField
from items.serializers.field_serializer import FieldSerializer, IntFieldSerializer, FloatFieldSerializer, \
    ShortTextFieldSerializer, LongTextFieldSerializer


def update_helper(client, serializer, serializer_type):
    field = client.get_object()
    old_serializer = serializer_type(field)
    serializer.save()
    item = client.get_object().item
    comment = serializer_compare_pretty_print(old_serializer=old_serializer, new_serializer=serializer,
                                              title="INT CUSTOM FIELD MODIFIED") + "item name : " + item.name
    LoggerUtility.log(initiating_user=client.request.user, nature_enum=ActionEnum.CUSTOM_FIELD_VALUE_MODIFIED,
                      comment=comment, items_affected=[item])


class FieldList(generics.ListCreateAPIView):
    queryset = Field.objects.all()
    permission_classes = [IsSuperUser]
    serializer_class = FieldSerializer

    def perform_create(self, serializer):
        serializer.save()
        comment = serializer_pretty_print(serializer=serializer, title=ActionEnum.CUSTOM_FIELD_CREATED.value)
        LoggerUtility.log(initiating_user=self.request.user, nature_enum=ActionEnum.CUSTOM_FIELD_CREATED,
                          comment=comment)


class FieldDeletion(generics.DestroyAPIView):
    queryset = Field.objects.all()
    permission_classes = [IsSuperUser]
    serializer_class = FieldSerializer

    def perform_destroy(self, instance):
        field_serializer = FieldSerializer(instance=instance)
        comment = serializer_pretty_print(serializer=field_serializer, title=ActionEnum.CUSTOM_FIELD_DELETED.value,
                                          validated=False)
        LoggerUtility.log(initiating_user=self.request.user, nature_enum=ActionEnum.CUSTOM_FIELD_DELETED,
                          comment=comment)
        instance.delete()


class IntFieldUpdate(generics.UpdateAPIView):
    queryset = IntField.objects.all()
    permission_classes = [IsStaffUser]
    serializer_class = IntFieldSerializer

    def perform_update(self, serializer):
        update_helper(self, serializer, IntFieldSerializer)


class FloatFieldUpdate(generics.UpdateAPIView):
    queryset = FloatField.objects.all()
    permission_classes = [IsStaffUser]
    serializer_class = FloatFieldSerializer

    def perform_update(self, serializer):
        update_helper(self, serializer, FloatFieldSerializer)


class ShortTextFieldUpdate(generics.UpdateAPIView):
    queryset = ShortTextField.objects.all()
    permission_classes = [IsStaffUser]
    serializer_class = ShortTextFieldSerializer

    def perform_update(self, serializer):
        update_helper(self, serializer, ShortTextFieldSerializer)


class LongTextFieldUpdate(generics.UpdateAPIView):
    queryset = LongTextField.objects.all()
    permission_classes = [IsStaffUser]
    serializer_class = LongTextFieldSerializer

    def perform_update(self, serializer):
        update_helper(self, serializer, LongTextFieldSerializer)
