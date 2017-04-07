from rest_framework import serializers

from inventory_requests.models import RequestCart, Loan
from inventory_requests.serializers.DisbursementSerializer import DisbursementSerializer, LoanSerializer
from django.db.models import Q


class RequestCartSerializer(serializers.ModelSerializer):
    staff = serializers.SlugRelatedField(read_only=True, many=False, slug_field='username')
    owner = serializers.SlugRelatedField(read_only=True, many=False, slug_field='username')
    cart_disbursements = DisbursementSerializer(read_only=True, many=True)
    #cart_loans = LoanSerializer(read_only=True, many=True)
    cart_loans = serializers.SerializerMethodField()
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

    def get_cart_loans(self, obj):
        q_func = ~Q(backfill_loan__status='backfill_satisfied')
        return LoanSerializer(Loan.objects.filter(q_func), many=True).data


class QuantitySerializer(serializers.Serializer):
    type = serializers.ChoiceField(choices=['loan','disbursement'], required=True)
    quantity = serializers.IntegerField(min_value=1, required=True)


class RequestTypeSerializer(serializers.Serializer):
    current_type = serializers.ChoiceField(choices=['loan', 'disbursement'], required=True)
    pk = serializers.IntegerField(min_value=1, required=True)
    quantity = serializers.IntegerField(min_value=1, required=False)

