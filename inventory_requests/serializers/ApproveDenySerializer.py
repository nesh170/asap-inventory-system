from rest_framework import serializers
from inventory_requests.models import RequestCart


class ApproveDenySerializer(serializers.ModelSerializer):
    staff = serializers.SlugRelatedField(read_only=True, many=False, slug_field='username')

    class Meta:
        model = RequestCart
        fields = ('id', 'status', 'staff_comment', 'staff_timestamp', 'staff')
