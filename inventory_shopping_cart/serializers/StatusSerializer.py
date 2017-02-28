from rest_framework import serializers
from inventory_shopping_cart.models import ShoppingCart


class StatusSerializer(serializers.ModelSerializer):
    admin = serializers.SlugRelatedField(read_only=True, many=False, slug_field='username')


    class Meta:
        model = ShoppingCart
        fields = ('id', 'admin_comment', 'admin_timestamp', 'admin')