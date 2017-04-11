from rest_framework import serializers

from inventory_requests.models import Backfill


class BackfillSerializer(serializers.ModelSerializer):
    #TODO make quantity required within serializer
    class Meta:
        model = Backfill
        fields = ('id', 'loan_id', 'status', 'quantity', 'pdf_url', 'timestamp')


#TODO add pdf support to this
class CreateBackfillSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=1, required=True)
    loan_id = serializers.IntegerField(min_value=1, required=True)
