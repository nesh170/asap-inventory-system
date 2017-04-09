from rest_framework import serializers
from rest_framework.exceptions import MethodNotAllowed

from inventoryProject.utility.queryset_functions import get_or_not_found, get_or_none
from inventory_requests.models import Loan, Disbursement
from inventory_requests.serializers.DisbursementSerializer import LoanSerializer, DisbursementSerializer
from items.factory.field_factory import AssetFieldFactory
from items.logic.asset_logic import create_asset_helper
from items.models.asset_custom_fields import AssetField
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

    def create(self, validated_data):
        item = get_or_not_found(Item, pk=validated_data.get('item_id'))
        asset = create_asset_helper(item=item)
        return asset
