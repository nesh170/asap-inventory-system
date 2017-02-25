from rest_framework import serializers

from inventory_disbursements.models import Cart
from inventory_shopping_cart.models import ShoppingCart
from inventory_transaction_logger.models import Log, Action, ItemLog, ShoppingCartLog, DisbursementCartLog
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

    class Meta:
        model = ItemLog
        fields = ('id', 'item')


class NestedShoppingCartSerializer(serializers.ModelSerializer):
    owner = serializers.SlugRelatedField(many=False, read_only=True, slug_field='username')

    class Meta:
        model = ShoppingCart
        fields = ('id', 'owner', 'status', 'reason', 'timestamp')


class ShoppingCartLogSerializer(serializers.ModelSerializer):
    shopping_cart = NestedShoppingCartSerializer(many=False, allow_null=False, read_only=True)

    class Meta:
        model = ShoppingCartLog
        fields = ('id', 'shopping_cart')


class NestedDisbursementCartSerializer(serializers.ModelSerializer):
    disburser = serializers.SlugRelatedField(many=False, read_only=True, slug_field='username')
    receiver = serializers.SlugRelatedField(many=False, read_only=True, slug_field='username')

    class Meta:
        model = Cart
        fields = ('id', 'disburser', 'comment', 'receiver', 'timestamp')


class DisbursementCartLogSerializer(serializers.ModelSerializer):
    cart = NestedDisbursementCartSerializer(many=False, allow_null=False, read_only=True)

    class Meta:
        model = DisbursementCartLog
        fields = ('id', 'cart')


class LogSerializer(serializers.ModelSerializer):
    initiating_user = serializers.SlugRelatedField(many=False, read_only=True, slug_field='username')
    nature = ActionSerializer(many=False, read_only=True)
    affected_user = serializers.SlugRelatedField(many=False, read_only=True, slug_field='username')
    item_log = ItemLogSerializer(read_only=True, many=True)
    shopping_cart_log = ShoppingCartLogSerializer(read_only=True, many=True)
    disbursement_log = DisbursementCartLogSerializer(read_only=True, many=True)

    class Meta:
        model = Log
        fields = ('id', 'initiating_user', 'nature', 'timestamp', 'affected_user', 'item_log',
                  'shopping_cart_log', 'comment', 'disbursement_log')
