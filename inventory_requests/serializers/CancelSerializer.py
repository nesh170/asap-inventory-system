from rest_framework import serializers
from inventory_requests.models import RequestCart


class CancelSerializer(serializers.ModelSerializer):
    comment = serializers.CharField(required=False)

    class Meta:
        model = RequestCart
        fields = ('id', 'comment')
