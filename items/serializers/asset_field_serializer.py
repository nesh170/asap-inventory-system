from rest_framework import serializers

from items.factory.field_factory import AssetFieldFactory
from items.models.asset_custom_fields import AssetField, IntAssetField, FloatAssetField, ShortTextAssetField, \
    LongTextAssetField


class AssetFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetField
        fields = ('id', 'name', 'type', 'private')

    def create(self, validated_data):
        field = AssetField.objects.create(**validated_data)
        factory = AssetFieldFactory()
        factory.create_asset_field_all_assets(field=field)
        return field


class IntAssetFieldSerializer(serializers.ModelSerializer):
    field = serializers.SlugRelatedField(read_only=True, slug_field='name')

    class Meta:
        model = IntAssetField
        fields = ('id', 'asset', 'field', 'value')


class FloatAssetFieldSerializer(serializers.ModelSerializer):
    field = serializers.SlugRelatedField(read_only=True, slug_field='name')

    class Meta:
        model = FloatAssetField
        fields = ('id', 'asset', 'field', 'value')


class ShortTextAssetFieldSerializer(serializers.ModelSerializer):
    field = serializers.SlugRelatedField(read_only=True, slug_field='name')

    class Meta:
        model = ShortTextAssetField
        fields = ('id', 'asset', 'field', 'value')


class LongTextAssetFieldSerializer(serializers.ModelSerializer):
    field = serializers.SlugRelatedField(read_only=True, slug_field='name')

    class Meta:
        model = LongTextAssetField
        fields = ('id', 'asset', 'field', 'value')