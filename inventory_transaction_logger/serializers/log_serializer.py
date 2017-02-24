from rest_framework import serializers
from inventory_transaction_logger.models import Log, Action, ItemLog
from inventory_user.serializers.user_serializer import UserSerializer
from items.models import Item

class ActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Action
        fields = ('id', 'color', 'tag')

class NestedItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ('id', 'name', 'quantity')

class ItemLogSerializer(serializers.ModelSerializer):
    item = NestedItemSerializer(many=False, allow_null=False, read_only=True)
    item_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = ItemLog
        fields = ('id', 'log_id', 'item', 'item_id')
class LogSerializer(serializers.ModelSerializer):
    nature_id = serializers.IntegerField(write_only=True)
    nature = ActionSerializer(many=False, read_only=True)
    initiating_user = UserSerializer(read_only=True, many=False)
    affected_user = UserSerializer(read_only=True, many=False)
    item_log = ItemLogSerializer(read_only=True, many=True)
    class Meta:
        model = Log
        fields = ('id', 'initiating_user', 'nature', 'nature_id', 'timestamp', 'affected_user', 'item_log')

    def create(self, validated_data):
        username = self.context.get("request").user.username
        action_id = validated_data.get("action_id")
        action = Action.objects.get(pk=action_id)
        return Log.objects.create(user=username, action=action, **validated_data)
