from rest_framework import serializers
from items.models import Tag


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'item', 'tag')


class TagSingleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('tag', )


class NestedTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'tag')

