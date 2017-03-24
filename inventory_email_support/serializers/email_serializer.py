from rest_framework import serializers
from inventory_email_support.models import SubjectTag, PrependedBody


class SubjectTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubjectTag
        fields = ('subject_tag', )
        extra_kwargs = {'subject_tag': {'required': True}}


class PrependedBodySerializer(serializers.ModelSerializer):
    class Meta:
        model = PrependedBody
        fields = ('prepended_body', )
        extra_kwargs = {'prepended_body': {'required': True}}