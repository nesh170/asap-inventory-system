from rest_framework import serializers


class DisburseSerializer(serializers.Serializer):
    item_id = serializers.IntegerField()
    quantity = serializers.IntegerField()
    receiver = serializers.CharField(max_length=200)
    disburse_comment = serializers.CharField()