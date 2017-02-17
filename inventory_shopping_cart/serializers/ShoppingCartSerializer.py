from django.contrib.auth.models import User
from rest_framework import serializers

from inventory_logger.action_enum import ActionEnum
from inventory_logger.utility.logger import LoggerUtility
from inventory_requests.models import Request
from inventory_user.serializers.user_serializer import UserSerializer
from items.models import Item


class NestedItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ('id', 'name', 'quantity')

class RequestSerializer(serializers.ModelSerializer):
    item = NestedItemSerializer(many=False, allow_null=False, read_only=True)
    item_id = serializers.IntegerField(required=True)
    admin = UserSerializer(read_only=True, many=False)
    owner = UserSerializer(read_only=True, many=False)
    extra_kwargs = {'item_id': {'write_only': True}}

    class Meta:
        model = Request
        fields = ('id', 'owner', 'status', 'reason', 'requests', 'timestamp', 'admin_timestamp', 'admin_comment', 'admin')

    def create(self, validated_data):
        item_id = validated_data.pop('item_id')
        item = Item.objects.get(pk=item_id)
        user = self.context['request'].user
        request = Request.objects.create(item=item, owner=user, **validated_data)
        LoggerUtility.log_as_system(ActionEnum.REQUEST_CREATED, "Request (ID: " + str(request.id) + ") Created")
        return request

    def update(self, instance, validated_data):
        instance.owner = validated_data.get('owner', instance.owner)
        instance.status = validated_data.get('status', instance.status)
        instance.item = validated_data.get('item', instance.item)
        instance.quantity = validated_data.get('quantity', instance.quantity)
        instance.reason = validated_data.get('reason', instance.reason)
        instance.timestamp = validated_data.get('timestamp', instance.timestamp)
        instance.admin_timestamp = validated_data.get('admin_timestamp', instance.admin_timestamp)
        instance.admin_comment = validated_data.get('admin_comment', instance.admin_comment)
        instance.admin = validated_data.get('admin', instance.admin)
        instance.save()
        return instance