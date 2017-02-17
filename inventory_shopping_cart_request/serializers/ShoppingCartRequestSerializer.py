from rest_framework import serializers
from inventory_shopping_cart_request.models import RequestTable
from items.models import Item
from inventory_shopping_cart.models import ShoppingCart

class NestedItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ('id', 'name', 'quantity')

class ShoppingCartRequestSerializer(serializers.ModelSerializer):
    item = NestedItemSerializer(many=False, allow_null=False, read_only=True)
    shopping_cart_id = serializers.IntegerField(required=True)
    item_id = serializers.IntegerField(required=True)
    extra_kwargs = {'item_id': {'write_only': True}}


    class Meta:
        model = RequestTable
        fields = ('id', 'item_id', 'item', 'quantity_requested', 'shopping_cart_id')

    def create(self, validated_data):
        item_id = validated_data.pop('item_id')
        shopping_cart_id = validated_data.pop('shopping_cart_id')
        item = Item.objects.get(pk=item_id)
        shopping_cart = ShoppingCart.objects.get(pk=shopping_cart_id)
        shopping_cart_request = RequestTable.objects.create(item=item, shopping_cart=shopping_cart, **validated_data)
        return shopping_cart_request