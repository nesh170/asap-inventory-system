from rest_framework import serializers

from inventory_transaction_logger.action_enum import ActionEnum
from inventory_transaction_logger.utility.logger import LoggerUtility
from items.models import Item, IntField, FloatField, ShortTextField, LongTextField
from items.serializers.field_serializer import IntFieldSerializer, FloatFieldSerializer, ShortTextFieldSerializer, \
    LongTextFieldSerializer
from items.serializers.tag_serializer import NestedTagSerializer


def get_values(table, is_staff, item, serializer_constructor):
    field = table.objects.filter(item=item) if is_staff \
        else table.objects.filter(field__private=False, item=item)
    serializer = serializer_constructor(instance=field, many=True)
    return serializer.data


class DetailedItemSerializer(serializers.ModelSerializer):
    tags = NestedTagSerializer(many=True, allow_null=True, required=False)
    int_fields = serializers.SerializerMethodField()
    float_fields = serializers.SerializerMethodField()
    short_text_fields = serializers.SerializerMethodField()
    long_text_fields = serializers.SerializerMethodField()

    def get_int_fields(self, obj):
        return get_values(IntField, self.context['request'].user.is_staff, obj, IntFieldSerializer)

    def get_float_fields(self, obj):
        return get_values(FloatField, self.context['request'].user.is_staff, obj, FloatFieldSerializer)

    def get_short_text_fields(self, obj):
        return get_values(ShortTextField, self.context['request'].user.is_staff, obj, ShortTextFieldSerializer)

    def get_long_text_fields(self, obj):
        return get_values(LongTextField, self.context['request'].user.is_staff, obj, LongTextFieldSerializer)

    class Meta:
        model = Item
        fields = ('id', 'name', 'quantity', 'model_number', 'description', 'tags', 'int_fields', 'float_fields',
                  'short_text_fields', 'long_text_fields')

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.quantity = validated_data.get('quantity', instance.quantity)
        instance.model_number = validated_data.get('model_number', instance.model_number)
        instance.description = validated_data.get('description', instance.description)
        instance.save()
        username = self.context['request'].user.username
        comment_string = "Item with name {name} with these changes: name: {name_change};" \
                                                             " quantity: {quantity_change}; model_number: {model_number_change};" \
                                                             " description: {description_change}".format
        comment = comment_string(name=instance.name, name_change=validated_data.get('name'), quantity_change=validated_data.get('quantity'),
                                 model_number_change=validated_data.get('model_number'), description_change=validated_data.get('description'))
        LoggerUtility.log(initiating_user=self.context['request'].user, nature_enum=ActionEnum.ITEM_MODIFIED, comment=comment, items_affected=[instance])
        return instance
