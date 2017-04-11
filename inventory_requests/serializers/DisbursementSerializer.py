from django.db.models import Q
from rest_framework import serializers
from rest_framework.exceptions import MethodNotAllowed

from inventoryProject.utility.queryset_functions import get_or_not_found
from inventory_requests.models import Disbursement, Loan, Backfill
from inventory_requests.models import RequestCart
from items.models.asset_models import Asset
from items.models.item_models import Item
from inventory_requests.serializers.BackfillSerializer import BackfillSerializer


class NestedItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ('id', 'name', 'quantity', 'is_asset')


class NestedAssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asset
        fields = ('id', 'asset_tag')


class DisbursementSerializer(serializers.ModelSerializer):
    item = NestedItemSerializer(many=False, allow_null=False, read_only=True)
    assets = NestedAssetSerializer(many=True, read_only=True, allow_null=True)
    item_id = serializers.IntegerField(required=True, write_only=True)
    cart_owner = serializers.SerializerMethodField()

    class Meta:
        model = Disbursement
        fields = ('id', 'item_id', 'item', 'quantity', 'cart_id', 'cart_owner', 'from_backfill', 'assets')
        extra_kwargs = {'quantity': {'required': True}}

    def create(self, validated_data):
        item_id = validated_data.pop('item_id')
        user = self.context['request'].user
        condition = (Q(staff=user) if user.is_staff else Q(owner=user)) & Q(status='active')
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

    def get_cart_owner(self, obj):
        return obj.cart.owner.username if obj.cart.owner is not None else None


class LoanSerializer(serializers.ModelSerializer):
    item = NestedItemSerializer(many=False, allow_null=False, read_only=True)
    assets = NestedAssetSerializer(many=True, read_only=True, allow_null=True)
    item_id = serializers.IntegerField(required=True, write_only=True)
    cart_owner = serializers.SerializerMethodField()
    backfill_loan = BackfillSerializer(many=True, read_only=True)

    class Meta:
        model = Loan
        fields = ('id', 'item_id', 'item', 'quantity', 'cart_id', 'cart_owner', 'loaned_timestamp',
                  'returned_timestamp', 'returned_quantity', 'backfill_loan', 'assets')
        extra_kwargs = {'quantity': {'required': True}}

    def create(self, validated_data):
        item_id = validated_data.pop('item_id')
        user = self.context['request'].user
        condition = (Q(staff=user) if user.is_staff else Q(owner=user)) & Q(status='active')
        if RequestCart.objects.filter(condition).exists():
            request_cart = RequestCart.objects.get(condition)
            item = get_or_not_found(Item, pk=item_id)
            if request_cart.cart_loans.filter(item=item).exists():
                raise MethodNotAllowed(self.create, "Item already exists in cart - cannot be added")
            else:
                loan = Loan.objects.create(item=item, cart=request_cart, **validated_data)
                return loan
        else:
            raise MethodNotAllowed(self.create, "Item must be added to active cart")

    def get_cart_owner(self, obj):
        return obj.cart.owner.username if obj.cart.owner is not None else None
