from django.contrib.auth.models import User
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'email', 'is_staff', 'last_login', 'date_joined')
        read_only_fields = ('last_login', 'date_joined')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        username = validated_data.get('username')
        password = validated_data.get('password')
        email = validated_data.get('email')
        is_staff = validated_data.get('is_staff')
        if is_staff:
            return User.objects.create_superuser(username=username, password=password, email=email)
        else:
            return User.objects.create_user(username=username, password=password, email=email)

