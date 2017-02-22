from rest_framework import serializers
from inventory_shopping_cart.models import ShoppingCart


class CancelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingCart
        fields = ('id', 'reason')