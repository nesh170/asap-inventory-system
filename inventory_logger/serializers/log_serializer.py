from rest_framework import serializers

from inventory_logger.models import Log


class LogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Log
        fields = ('id', 'user', 'action', 'timestamp', 'description')
        read_only_fields = ('user',)

    def create(self, validated_data):
        username = self.context.get("request").user.username
        return Log.objects.create(user=username, **validated_data)
