from django.contrib.auth.models import User
from oauth2_provider.ext.rest_framework import TokenHasReadWriteScope
from rest_framework import generics
from rest_framework.permissions import IsAdminUser

from inventory_user.serializers.user_serializer import UserSerializer


class InventoryUserList(generics.ListCreateAPIView):
    permission_classes = [IsAdminUser, TokenHasReadWriteScope]
    queryset = User.objects.all()
    serializer_class = UserSerializer
