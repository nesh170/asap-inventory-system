from rest_framework import serializers

from inventory_logger.models import Log


class LogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Log
        fields = ('id', 'user', 'action', 'timestamp', 'log_text')
