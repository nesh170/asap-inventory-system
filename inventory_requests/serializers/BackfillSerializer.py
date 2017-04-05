from rest_framework import serializers
from inventory_requests.serializers.DisbursementSerializer import NestedItemSerializer

from inventory_requests.models import Backfill

class BackfillSerializer(serializers.ModelSerializer):
    item = NestedItemSerializer(many=False, allow_null=False, read_only=True)
    item_id = serializers.IntegerField(required=True, write_only=True)
    cart_owner = serializers.SerializerMethodField()

    class Meta:
        model = Backfill
        fields = ('id', 'item_id', 'item', 'quantity', 'cart_id', 'cart_owner', 'pdf_url')

    def get_cart_owner(self, obj):
        return obj.cart.owner.username if obj.cart.owner is not None else None

#TODO add pdf support to this
class LoanToBackfillSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=1, required=True)
    pk = serializers.IntegerField(min_value=1, required=True)
