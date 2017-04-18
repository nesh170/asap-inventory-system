from rest_framework import serializers

from inventory_requests.models import Backfill


class BackfillSerializer(serializers.ModelSerializer):
    cart_id = serializers.SerializerMethodField()
    cart_owner = serializers.SerializerMethodField()

    class Meta:
        model = Backfill
        fields = ('id', 'loan_id', 'status', 'quantity', 'pdf_url', 'file_name', 'timestamp', 'cart_id', 'cart_owner')

    def get_cart_id(self, obj):
        return obj.loan.cart.id

    def get_cart_owner(self, obj):
        return obj.loan.cart.owner.username

class UpdateBackfillSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=1, required=False)
    backfill_id = serializers.IntegerField(min_value=1, required=True)


class CreateBackfillSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=1, required=True)
    loan_id = serializers.IntegerField(min_value=1, required=True)
