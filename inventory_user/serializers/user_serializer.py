from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.exceptions import ParseError


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'email', 'is_staff', 'is_superuser', 'last_login', 'date_joined')
        read_only_fields = ('last_login', 'date_joined')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        username = validated_data.get('username')
        password = make_password(validated_data.get('password'), hasher='pbkdf2_sha256')
        email = validated_data.get('email')
        is_staff = validated_data.get('is_staff', False)
        is_superuser = validated_data.get('is_superuser', False)
        try:
            user = User.objects.create_superuser(username=username, password=password, email=email) \
                if is_superuser else User.objects.create(username=username, password=password, email=email,
                                                         is_staff=is_staff)
        except ValueError:
            raise ParseError(detail="Both is_staff and is_superuser has to be true for admin creation")
        return user


class LargeUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username',)

