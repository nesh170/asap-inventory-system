from rest_framework import serializers
from rest_framework.exceptions import MethodNotAllowed

from inventoryProject.utility.queryset_functions import get_or_not_found, get_or_none
from inventory_requests.models import Loan, Disbursement
from inventory_requests.serializers.DisbursementSerializer import LoanSerializer, DisbursementSerializer
from items.models.asset_custom_fields import IntAssetField, FloatAssetField, ShortTextAssetField, LongTextAssetField
from items.models.asset_models import Asset
from items.serializers.asset_field_serializer import LongTextAssetFieldSerializer, ShortTextAssetFieldSerializer, \
    FloatAssetFieldSerializer, IntAssetFieldSerializer


def get_values(table, is_staff, asset, serializer_constructor):
    field = table.objects.filter(asset=asset) if is_staff \
        else table.objects.filter(field__private=False, asset=asset)
    serializer = serializer_constructor(instance=field, many=True)
    return serializer.data


class DetailedAssetSerializer(serializers.ModelSerializer):
    loan = LoanSerializer(many=False, allow_null=True, required=False, read_only=True)
    disbursement = DisbursementSerializer(many=False, allow_null=True, required=False, read_only=True)
    loan_id = serializers.IntegerField(write_only=True, min_value=1, required=False)
    disbursement_id = serializers.IntegerField(write_only=True, min_value=1, required=False)
    item_id = serializers.IntegerField(min_value=1)
    int_fields = serializers.SerializerMethodField()
    float_fields = serializers.SerializerMethodField()
    short_text_fields = serializers.SerializerMethodField()
    long_text_fields = serializers.SerializerMethodField()

    def get_int_fields(self, obj):
        return get_values(IntAssetField, self.context['request'].user.is_staff, obj, IntAssetFieldSerializer)

    def get_float_fields(self, obj):
        return get_values(FloatAssetField, self.context['request'].user.is_staff, obj, FloatAssetFieldSerializer)

    def get_short_text_fields(self, obj):
        return get_values(ShortTextAssetField, self.context['request'].user.is_staff, obj, ShortTextAssetFieldSerializer)

    def get_long_text_fields(self, obj):
        return get_values(LongTextAssetField, self.context['request'].user.is_staff, obj, LongTextAssetFieldSerializer)

    class Meta:
        model = Asset
        fields = ('id', 'asset_tag', 'loan', 'disbursement', 'loan_id', 'disbursement_id', 'item_id', 'int_fields',
                  'float_fields', 'short_text_fields', 'long_text_fields',)
        extra_kwargs = {'asset_tag': {'required': False}}

    def update(self, instance, validated_data):
        loan_id = validated_data.get('loan_id')
        disbursement_id = validated_data.get('disbursement_id')
        if loan_id or disbursement_id:
            if (loan_id and disbursement_id) or instance.disbursement or instance.loan:
                raise MethodNotAllowed(method=self.update, detail='Cannot put in both disbursement and loan')
            if loan_id:
                instance.loan = get_or_not_found(Loan, pk=loan_id)
            if disbursement_id:
                instance.disbursement = get_or_not_found(Disbursement, pk=disbursement_id)
        asset_tag = validated_data.get('asset_tag')
        if asset_tag and get_or_none(Asset, asset_tag=asset_tag):
            raise MethodNotAllowed(method=self.update, detail="{asset_tag} is not unique".format(asset_tag=asset_tag))
        instance.asset_tag = validated_data.get('asset_tag', instance.asset_tag)
        instance.save()
        return instance

