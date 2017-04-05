from rest_framework import serializers
from inventory_requests.serializers.DisbursementSerializer import NestedItemSerializer

from inventory_requests.models import Backfill


class BackfillSerializer(serializers.ModelSerializer):
    #TODO make quantity required within serializer
    class Meta:
        model = Backfill
        fields = ('id', 'loan_id', 'quantity', 'pdf_url', 'status')


#TODO add pdf support to this
class LoanToBackfillSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=1, required=True)
    pk = serializers.IntegerField(min_value=1, required=True)
