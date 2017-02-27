from rest_framework import serializers

from inventory_shopping_cart.models import ShoppingCart
from inventory_shopping_cart_request.serializers.ShoppingCartRequestSerializer import ShoppingCartRequestSerializer


class ShoppingCartSerializer(serializers.ModelSerializer):
    admin = serializers.SlugRelatedField(read_only=True, many=False, slug_field='username')
    owner = serializers.SlugRelatedField(read_only=True, many=False, slug_field='username')
    requests = ShoppingCartRequestSerializer(read_only=True, many=True)
    reason = serializers.CharField(required=True)

    class Meta:
        model = ShoppingCart
        fields = ('id', 'owner', 'status', 'reason', 'requests', 'timestamp', 'admin_timestamp', 'admin_comment', 'admin')

    def create(self, validated_data):
        user = self.context['request'].user
        shopping_cart = ShoppingCart.objects.create(owner=user, **validated_data)
        return shopping_cart