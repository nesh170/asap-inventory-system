from rest_framework import serializers
from inventory_requests.models import Request


class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Request
        fields = ('id', 'admin_comment')