from rest_framework import serializers
from inventory_requests.models import Request


class CancelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Request
        fields = ('id', 'reason')