from rest_framework import serializers
from inventory_transaction_logger.models import Log, Action, ItemLog, ShoppingCartLog
from inventory_shopping_cart.models import ShoppingCart
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


class NestedShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingCart
        fields = ('id', 'owner', 'status', 'reason', 'timestamp')

class ShoppingCartLogSerializer(serializers.ModelSerializer):
    shopping_cart = NestedShoppingCartSerializer(many=False, allow_null=False, read_only=True)
    shopping_cart_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = ShoppingCartLog
        fields = ('id', 'log_id', 'shopping_cart', 'shopping_cart_id')

class LogSerializer(serializers.ModelSerializer):
    nature_id = serializers.IntegerField(write_only=True)
    nature = ActionSerializer(many=False, read_only=True)
    initiating_user = serializers.SlugRelatedField(many=False, read_only=True, slug_field='username')
    affected_user = serializers.SlugRelatedField(many=False, read_only=True, slug_field='username')
    item_log = ItemLogSerializer(read_only=True, many=True)
    shopping_cart_log = ShoppingCartLogSerializer(read_only=True, many=True)


    class Meta:
        model = Log
        fields = ('id', 'initiating_user', 'nature', 'nature_id', 'timestamp', 'affected_user', 'item_log', 'shopping_cart_log', 'comment')