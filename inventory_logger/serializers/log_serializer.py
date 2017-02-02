from rest_framework import serializers

from inventory_logger.models import Log, Action


class ActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Action
        fields = ('id', 'color', 'tag')


class LogSerializer(serializers.ModelSerializer):
    action_id = serializers.IntegerField(write_only=True)
    action = ActionSerializer(many=False, read_only=True)

    class Meta:
        model = Log
        fields = ('id', 'user', 'action', 'action_id', 'timestamp', 'description')
        read_only_fields = ('user', 'action')

    def create(self, validated_data):
        username = self.context.get("request").user.username
        action_id = validated_data.get("action_id")
        action = Action.objects.get(pk=action_id)
        return Log.objects.create(user=username, action=action, **validated_data)
