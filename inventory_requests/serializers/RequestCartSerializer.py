from rest_framework import serializers

from inventoryProject.utility.queryset_functions import get_or_not_found
from inventory_requests.models import RequestCart
from inventory_requests.serializers.DisbursementSerializer import DisbursementSerializer, LoanSerializer
from items.models.asset_models import ASSET_TAG_MAX_LENGTH, Asset


class RequestCartSerializer(serializers.ModelSerializer):
    staff = serializers.SlugRelatedField(read_only=True, many=False, slug_field='username')
    owner = serializers.SlugRelatedField(read_only=True, many=False, slug_field='username')
    cart_disbursements = DisbursementSerializer(read_only=True, many=True)
    cart_loans = LoanSerializer(read_only=True, many=True)
    reason = serializers.CharField(required=True)

    class Meta:
        model = RequestCart
        fields = ('id', 'owner', 'status', 'reason', 'cart_disbursements', 'cart_loans', 'timestamp', 'staff_timestamp',
                  'staff_comment', 'staff')

    def create(self, validated_data):
        user = self.context['request'].user
        request_cart = RequestCart.objects.create(staff=user, **validated_data) if user.is_staff else \
            RequestCart.objects.create(owner=user, **validated_data)
        return request_cart


class QuantitySerializer(serializers.Serializer):
    type = serializers.ChoiceField(choices=['loan','disbursement'], required=True)
    quantity = serializers.IntegerField(min_value=1, required=True)


class RequestTypeSerializer(serializers.Serializer):
    current_type = serializers.ChoiceField(choices=['loan', 'disbursement'], required=True)
    pk = serializers.IntegerField(min_value=1, required=True)
    quantity = serializers.IntegerField(min_value=1, required=False)
    asset_id = serializers.IntegerField(min_value=1, required=False)

    def validate(self, attrs):
        if attrs.get('quantity') and attrs.get('asset_id'):
            raise serializers.ValidationError("Cannot Have Both Asset Id and Quantity")
        return attrs

