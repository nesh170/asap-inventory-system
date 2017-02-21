from rest_framework import serializers
from inventory_shopping_cart_request.models import RequestTable
from items.models import Item
from inventory_shopping_cart.models import ShoppingCart
from rest_framework.exceptions import MethodNotAllowed


class NestedItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ('id', 'name', 'quantity')

class ShoppingCartRequestSerializer(serializers.ModelSerializer):
    item = NestedItemSerializer(many=False, allow_null=False, read_only=True)
    item_id = serializers.IntegerField(required=True)
    extra_kwargs = {'item_id': {'write_only': True}}


    class Meta:
        model = RequestTable
        fields = ('id', 'item_id', 'item', 'quantity_requested', 'shopping_cart_id')

    def create(self, validated_data):
        item_id = validated_data.pop('item_id')
        quantity_requested = validated_data.pop('quantity_requested')
        shopping_cart_id = ShoppingCart.objects.filter(owner=self.context['request'].user).get(status='active').id
        item = Item.objects.get(pk=item_id)
        shopping_cart = ShoppingCart.objects.get(pk=shopping_cart_id)
        #TODO fix this - throws exception properly, but returns 500 internal server error, don't want to throw a 500
        if (shopping_cart.requests.filter(item=item).exists()):
            raise MethodNotAllowed(self.create, "Item already exists in cart - cannot be added")
        elif (quantity_requested < 0):
            raise MethodNotAllowed(self.create, "Quantity must be greater than or equal to 0")
        else:
            shopping_cart_request = RequestTable.objects.create(item=item, shopping_cart=shopping_cart, **validated_data)
            return shopping_cart_request