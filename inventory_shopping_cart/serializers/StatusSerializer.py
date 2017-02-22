from rest_framework import serializers
from inventory_shopping_cart.models import ShoppingCart


class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingCart
        fields = ('id', 'admin_comment', 'admin_timestamp', 'admin')