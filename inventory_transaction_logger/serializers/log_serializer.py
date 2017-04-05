from rest_framework import serializers

from inventory_requests.models import RequestCart
from inventory_transaction_logger.models import Log, Action, ItemLog, RequestCartLog
from items.models.item_models import Item


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

    class Meta:
        model = ItemLog
        fields = ('id', 'item')


class NestedRequestCartSerializer(serializers.ModelSerializer):
    owner = serializers.SlugRelatedField(many=False, read_only=True, slug_field='username')

    class Meta:
        model = RequestCart
        fields = ('id', 'owner', 'status', 'reason', 'timestamp')


class RequestCartLogSerializer(serializers.ModelSerializer):
    request_cart = NestedRequestCartSerializer(many=False, allow_null=False, read_only=True)

    class Meta:
        model = RequestCartLog
        fields = ('id', 'request_cart')


class LogSerializer(serializers.ModelSerializer):
    initiating_user = serializers.SlugRelatedField(many=False, read_only=True, slug_field='username')
    nature = ActionSerializer(many=False, read_only=True)
    affected_user = serializers.SlugRelatedField(many=False, read_only=True, slug_field='username')
    item_log = ItemLogSerializer(read_only=True, many=True)
    request_cart_log = RequestCartLogSerializer(read_only=True, many=True)

    class Meta:
        model = Log
        fields = ('id', 'initiating_user', 'nature', 'timestamp', 'affected_user', 'item_log',
                  'request_cart_log', 'comment')
