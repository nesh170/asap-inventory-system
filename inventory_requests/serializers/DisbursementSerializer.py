from django.db.models import Q
from rest_framework import serializers

from inventoryProject.utility.queryset_functions import get_or_not_found
from inventory_requests.models import Disbursement
from items.models import Item
from inventory_requests.models import RequestCart
from rest_framework.exceptions import MethodNotAllowed


class NestedItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ('id', 'name', 'quantity')


class DisbursementSerializer(serializers.ModelSerializer):
    item = NestedItemSerializer(many=False, allow_null=False, read_only=True)
    item_id = serializers.IntegerField(required=True, write_only=True)

    class Meta:
        model = Disbursement
        fields = ('id', 'item_id', 'item', 'quantity', 'cart_id')
        extra_kwargs = {'quantity': {'required': True}}

    def create(self, validated_data):
        item_id = validated_data.pop('item_id')
        user = self.context['request'].user
        condition = (Q(owner=user) | Q(staff=user)) & Q(status='active')
        if RequestCart.objects.filter(condition).exists():
            request_cart = RequestCart.objects.get(condition)
            item = get_or_not_found(Item, pk=item_id)
            if request_cart.cart_disbursements.filter(item=item).exists():
                raise MethodNotAllowed(self.create, "Item already exists in cart - cannot be added")
            else:
                disbursement = Disbursement.objects.create(item=item, cart=request_cart, **validated_data)
                return disbursement
        else:
            raise MethodNotAllowed(self.create, "Item must be added to active cart")
