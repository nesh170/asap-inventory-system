from rest_framework import serializers
from inventory_email_support.models import SubscribedManagers, SubjectTag, PrependedBody, LoanReminderSchedule
from django.contrib.auth.models import User


class SubjectTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubjectTag
        fields = ('subject_tag', )
        extra_kwargs = {'subject_tag': {'required': True}}


class NestedUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email')


class SubscribedManagerSerializer(serializers.ModelSerializer):
    member = NestedUserSerializer(many=False, read_only=True)

    class Meta:
        model = SubscribedManagers
        fields = ('id', 'member')


class PrependedBodySerializer(serializers.ModelSerializer):
    class Meta:
        model = PrependedBody
        fields = ('prepended_body', )
        extra_kwargs = {'prepended_body': {'required': True}}


class LoanReminderScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanReminderSchedule
        fields = ('id', 'date', 'executed')
