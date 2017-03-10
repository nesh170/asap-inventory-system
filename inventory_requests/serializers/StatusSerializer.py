from rest_framework import serializers
from inventory_requests.models import RequestCart


class StatusSerializer(serializers.ModelSerializer):
    staff = serializers.SlugRelatedField(read_only=True, many=False, slug_field='username')

    class Meta:
        model = RequestCart
        fields = ('id', 'staff_comment', 'staff_timestamp', 'staff')
