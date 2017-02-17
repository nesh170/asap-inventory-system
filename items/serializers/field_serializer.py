from rest_framework import serializers

from items.factory.field_factory import FieldFactory
from items.models import Field, IntField, FloatField, ShortTextField, LongTextField


class FieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = Field
        fields = ('id', 'name', 'type', 'private')

    def create(self, validated_data):
        field = Field.objects.create(**validated_data)
        factory = FieldFactory()
        factory.create_field_all_items(field=field)
        return field


class IntFieldSerializer(serializers.ModelSerializer):
    field_id = serializers.IntegerField()
    item_id = serializers.IntegerField()
    field = serializers.SlugRelatedField(read_only=True, slug_field='name')

    class Meta:
        model = IntField
        fields = ('id', 'item', 'field', 'value', 'field_id', 'item_id')
        extra_kwargs = {'field_id': {'write_only': True}, 'item_id': {'write_only': True}}


class FloatFieldSerializer(serializers.ModelSerializer):
    field_id = serializers.IntegerField()
    item_id = serializers.IntegerField()
    field = serializers.SlugRelatedField(read_only=True, slug_field='name')

    class Meta:
        model = FloatField
        fields = ('id', 'item', 'field', 'value', 'field_id', 'item_id')
        extra_kwargs = {'field_id': {'write_only': True}, 'item_id': {'write_only': True}}


class ShortTextFieldSerializer(serializers.ModelSerializer):
    field_id = serializers.IntegerField()
    item_id = serializers.IntegerField()
    field = serializers.SlugRelatedField(read_only=True, slug_field='name')

    class Meta:
        model = ShortTextField
        fields = ('id', 'item', 'field', 'value', 'field_id', 'item_id')
        extra_kwargs = {'field_id': {'write_only': True}, 'item_id': {'write_only': True}}


class LongTextFieldSerializer(serializers.ModelSerializer):
    field_id = serializers.IntegerField()
    item_id = serializers.IntegerField()
    field = serializers.SlugRelatedField(read_only=True, slug_field='name')

    class Meta:
        model = LongTextField
        fields = ('id', 'item', 'field', 'value', 'field_id', 'item_id')
        extra_kwargs = {'field_id': {'write_only': True}, 'item_id': {'write_only': True}}