from rest_framework import serializers

from inventory_logger.action_enum import ActionEnum
from inventory_logger.utility.logger import LoggerUtility
from items.models import Item, Tag


class NestedTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'tag')


class ItemSerializer(serializers.ModelSerializer):
    tags = NestedTagSerializer(many=True, allow_null=True, required=False)

    class Meta:
        model = Item
        fields = ('id', 'name', 'quantity', 'model_number', 'description', 'location', 'tags')

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
        username = self.context['request'].user.username
        LoggerUtility.log_as_system(ActionEnum.ITEM_CREATED, username + " Created New Item:" + item.__str__())
        return item

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.quantity = validated_data.get('quantity', instance.quantity)
        instance.model_number = validated_data.get('model_number', instance.model_number)
        instance.description = validated_data.get('description', instance.description)
        instance.location = validated_data.get('location', instance.location)
        instance.save()
        username = self.context['request'].user.username
        LoggerUtility.log_as_system(ActionEnum.ITEM_MODIFIED, username + " Modified Item:" + instance.name)
        return instance

