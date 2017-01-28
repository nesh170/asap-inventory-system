from rest_framework import serializers
from requests.models import Request
class RequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Request
        fields = ('id', 'owner', 'status', 'item', 'quantity', 'reason', 'timestamp', 'admin_timestamp', 'system_comment', 'admin_comment', 'admin')