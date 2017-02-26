from django.contrib.auth.models import User
from rest_framework import serializers

from inventory_disbursements.models import Disbursement, Cart
from items.models import Item


class NestedUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username')


class NestedItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ('id', 'name', 'quantity')


class DisbursementSerializer(serializers.ModelSerializer):
    item = NestedItemSerializer(read_only=True)
    item_id = serializers.IntegerField(write_only=True)
    cart_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Disbursement
        fields = ('id', 'item', 'quantity', 'item_id', 'cart_id')


class CartSerializer(serializers.ModelSerializer):
    disburser = NestedUserSerializer(read_only=True, many=False)
    receiver = NestedUserSerializer(read_only=True, many=False)
    disbursements = DisbursementSerializer(read_only=True, many=True)
    receiver_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Cart
        fields = ('id', 'disburser', 'receiver', 'comment', 'disbursements', 'receiver_id')