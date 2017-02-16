from rest_framework import serializers

from inventory_logger.action_enum import ActionEnum
from inventory_logger.utility.logger import LoggerUtility
from items.factory.field_factory import FieldFactory
from items.models import Item, Tag, Field
from items.serializers.tag_serializer import NestedTagSerializer


def create_fields(item):
    factory = FieldFactory()
    fields = Field.objects.all()
    [factory.create_field(field, item) for field in fields]


class UniqueItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ('id', 'name')


class ItemSerializer(serializers.ModelSerializer):
    tags = NestedTagSerializer(many=True, allow_null=True, required=False)

    class Meta:
        model = Item
        fields = ('id', 'name', 'quantity', 'model_number', 'description', 'tags')

    def create(self, validated_data):
        item = None
        try:
            tags_data = validated_data.pop('tags')
            item = Item.objects.create(**validated_data)
            if tags_data is not None:
                for tag in tags_data:
                    Tag.objects.create(item=item, **tag)
        except KeyError:
            item = Item.objects.create(**validated_data)
        create_fields(item)
        username = self.context['request'].user.username
        LoggerUtility.log_as_system(ActionEnum.ITEM_CREATED, username + " Created New Item:" + item.__str__())
        return item




