from rest_framework import generics

from inventoryProject.permissions import IsSuperUser, IsStaffUser
from inventory_transaction_logger.utility.logger import LoggerUtility
from inventory_transaction_logger.action_enum import ActionEnum
from items.models import Field, IntField, FloatField, ShortTextField, LongTextField
from items.serializers.field_serializer import FieldSerializer, IntFieldSerializer, FloatFieldSerializer, \
    ShortTextFieldSerializer, LongTextFieldSerializer


class FieldList(generics.ListCreateAPIView):
    queryset = Field.objects.all()
    permission_classes = [IsSuperUser]
    serializer_class = FieldSerializer

    def perform_create(self, serializer):
        data = serializer.validated_data
        private = data.get('private', False)
        comment_string = "Custom Field created with the following parameters: Name {name}; Type: {type}; Private: {private}".format
        comment = comment_string(name=data.get('name'), type=data.get('type'), private=private)
        LoggerUtility.log(initiating_user=self.request.user, nature_enum=ActionEnum.CUSTOM_FIELD_CREATED, comment=comment)
        serializer.save()


class FieldDeletion(generics.DestroyAPIView):
    queryset = Field.objects.all()
    permission_classes = [IsSuperUser]
    serializer_class = FieldSerializer

    def perform_destroy(self, instance):
        comment_string = "Custom Field deleted that had the following parameters: Name {name}; Type: {type}; Private: {private}".format
        comment = comment_string(name=instance.name, type=instance.type, private=instance.private)
        LoggerUtility.log(initiating_user=self.request.user, nature_enum=ActionEnum.CUSTOM_FIELD_DELETED, comment=comment)
        instance.delete()


class IntFieldUpdate(generics.UpdateAPIView):
    queryset = IntField.objects.all()
    permission_classes = [IsStaffUser]
    serializer_class = IntFieldSerializer

    def perform_update(self, serializer):
        item = self.get_object().item
        field_name = self.get_object().field.name
        data = serializer.validated_data
        comment_string = "Int Custom Field with name {name} has an updated value of {value} for item {item_name}".format
        comment = comment_string(name=field_name, value=data.get('value'), item_name=item.name)
        LoggerUtility.log(initiating_user=self.request.user, nature_enum=ActionEnum.CUSTOM_FIELD_VALUE_MODIFIED, comment=comment, items_affected=[item])
        serializer.save()


class FloatFieldUpdate(generics.UpdateAPIView):
    queryset = FloatField.objects.all()
    permission_classes = [IsStaffUser]
    serializer_class = FloatFieldSerializer

    def perform_update(self, serializer):
        #updated value in value field in serializer
        item = self.get_object().item
        field_name = self.get_object().field.name
        data = serializer.validated_data
        comment_string = "Float Custom Field with name {name} has an updated value of {value} for item {item_name}".format
        comment = comment_string(name=field_name, value=data.get('value'), item_name=item.name)
        LoggerUtility.log(initiating_user=self.request.user, nature_enum=ActionEnum.CUSTOM_FIELD_VALUE_MODIFIED, comment=comment, items_affected=[item])
        serializer.save()


class ShortTextFieldUpdate(generics.UpdateAPIView):
    queryset = ShortTextField.objects.all()
    permission_classes = [IsStaffUser]
    serializer_class = ShortTextFieldSerializer

    def perform_update(self, serializer):
        item = self.get_object().item
        field_name = self.get_object().field.name
        data = serializer.validated_data
        comment_string = "Short Text Custom Field with name {name} has an updated value of {value} for item {item_name}".format
        comment = comment_string(name=field_name, value=data.get('value'), item_name=item.name)
        LoggerUtility.log(initiating_user=self.request.user, nature_enum=ActionEnum.CUSTOM_FIELD_VALUE_MODIFIED, comment=comment, items_affected=[item])
        serializer.save()



class LongTextFieldUpdate(generics.UpdateAPIView):
    queryset = LongTextField.objects.all()
    permission_classes = [IsStaffUser]
    serializer_class = LongTextFieldSerializer

    def perform_update(self, serializer):
        item = self.get_object().item
        field_name = self.get_object().field.name
        data = serializer.validated_data
        comment_string = "Long Text Custom Field with name {name} has an updated value of {value} for item {item_name}".format
        comment = comment_string(name=field_name, value=data.get('value'), item_name=item.name)
        LoggerUtility.log(initiating_user=self.request.user, nature_enum=ActionEnum.CUSTOM_FIELD_VALUE_MODIFIED, comment=comment, items_affected=[item])
        serializer.save()