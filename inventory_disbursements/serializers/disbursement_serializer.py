from django.contrib.auth.models import User
from rest_framework import serializers

from inventory_disbursements.models import Disbursement
from inventory_logger.action_enum import ActionEnum
from inventory_logger.utility.logger import LoggerUtility
from items.models import Item


class NestedUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username')


class NestedItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ('id','name','quantity')


class DisbursementSerializer(serializers.ModelSerializer):
    disburser = NestedUserSerializer(read_only=True, many=False)
    item = NestedItemSerializer(read_only=True, many=False)
    receiver = NestedUserSerializer(read_only=True, many=False)
    item_id = serializers.IntegerField(required=True)
    receiver_id = serializers.IntegerField(required=True)

    class Meta:
        model = Disbursement
        fields = ('id', 'disburser', 'item', 'quantity', 'timestamp', 'receiver', 'item_id', 'receiver_id', )
        extra_kwargs = {'item_id': {'write_only': True},
                        'receiver_id': {'write_only': True}}

    def create(self, validated_data):
        disburser = self.context['request'].user
        disbursement = Disbursement.objects.create(disburser=disburser, **validated_data)
        LoggerUtility.log_as_system(ActionEnum.DISBURSED, disbursement.__str__())
        return disbursement

