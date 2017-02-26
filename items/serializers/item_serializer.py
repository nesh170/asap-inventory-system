from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from rest_framework.exceptions import NotFound, MethodNotAllowed, ParseError

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


class ItemQuantitySerializer(serializers.Serializer):
    item_id = serializers.IntegerField(required=True)
    quantity = serializers.IntegerField(required=True)
    comment = serializers.CharField(required=False)

    def create(self, validated_data):
        user = self.context['request'].user
        try:
            item = Item.objects.get(pk=validated_data.get('item_id'))
        except ObjectDoesNotExist:
            raise NotFound(detail="Item is not found in Database")
        quantity = validated_data.get('quantity', 0)
        comment = validated_data.get('comment', "No Comment")
        if quantity < 0:
            # TODO: log destruction here later with comments
            print('LOG DESTRUCTION' + comment)
        elif quantity > 0:
            # TODO: log accquisition here later with comments
            print('LOG ACCQUISITION' + comment)
        else:
            raise ParseError(detail="Quantity must be a nonzero value")
        item.quantity = item.quantity + quantity
        if item.quantity < 0:
            raise ParseError(detail="Updated item quantity cannot be below 0")
        item.save()
        return item

    def update(self, instance, validated_data):
        raise MethodNotAllowed(detail="Update is not allowed", method=self.update)


