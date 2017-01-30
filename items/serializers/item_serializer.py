from rest_framework import serializers
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
        try:
            tags_data = validated_data.pop('tags')
            item = Item.objects.create(**validated_data)
            for tag in tags_data:
                Tag.objects.create(item=item, **tag)
        except KeyError:
            item = Item.objects.create(**validated_data)
        return item

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.quantity = validated_data.get('quantity', instance.quantity)
        instance.model_number = validated_data.get('model_number', instance.model_number)
        instance.description = validated_data.get('description', instance.description)
        instance.location = validated_data.get('location', instance.location)
        instance.save()
        return instance
