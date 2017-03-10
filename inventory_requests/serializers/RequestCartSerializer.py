from rest_framework import serializers

from inventory_requests.models import RequestCart
from inventory_requests.serializers.DisbursementSerializer import DisbursementSerializer


class RequestCartSerializer(serializers.ModelSerializer):
    staff = serializers.SlugRelatedField(read_only=True, many=False, slug_field='username')
    owner = serializers.SlugRelatedField(read_only=True, many=False, slug_field='username')
    cart_disbursements = DisbursementSerializer(read_only=True, many=True)
    # add loan serializer here
    reason = serializers.CharField(required=True)

    class Meta:
        model = RequestCart
        fields = ('id', 'owner', 'status', 'reason', 'cart_disbursements', 'timestamp', 'staff_timestamp',
                  'staff_comment', 'staff')

    def create(self, validated_data):
        user = self.context['request'].user
        request_cart = RequestCart.objects.create(owner=user, **validated_data)
        return request_cart
