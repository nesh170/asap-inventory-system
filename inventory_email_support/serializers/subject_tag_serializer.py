from rest_framework import serializers
from inventory_email_support.models import SubjectTag


class SubjectTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubjectTag
        fields = ('subject_tag', )
        extra_kwargs = {'subject_tag': {'required': True}}

