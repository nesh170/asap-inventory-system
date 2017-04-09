from rest_framework import serializers
from rest_framework.exceptions import MethodNotAllowed

from inventoryProject.utility.queryset_functions import get_or_not_found, get_or_none
from inventory_requests.models import Loan, Disbursement
from inventory_requests.serializers.DisbursementSerializer import LoanSerializer, DisbursementSerializer
from items.logic.asset_logic import create_asset_helper
from items.models.asset_models import Asset
from items.models.item_models import Item


class AssetSerializer(serializers.ModelSerializer):
    loan = LoanSerializer(many=False, allow_null=True, required=False, read_only=True)
    disbursement = DisbursementSerializer(many=False, allow_null=True, required=False, read_only=True)
    loan_id = serializers.IntegerField(write_only=True, min_value=1, required=False)
    disbursement_id = serializers.IntegerField(write_only=True, min_value=1, required=False)
    item_id = serializers.IntegerField(min_value=1)

    class Meta:
        model = Asset
        fields = ('id', 'asset_tag', 'loan', 'disbursement', 'loan_id', 'disbursement_id', 'item_id', )
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

    def create(self, validated_data):
        item = get_or_not_found(Item, pk=validated_data.get('item_id'))
        asset = create_asset_helper(item=item)
        return asset
