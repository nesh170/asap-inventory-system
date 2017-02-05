from django.contrib.auth.models import User
from oauth2_provider.ext.rest_framework import TokenHasReadWriteScope
from rest_framework import generics
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from inventory_user.serializers.user_serializer import UserSerializer


class InventoryUserList(generics.ListCreateAPIView):
    permission_classes = [IsAdminUser, TokenHasReadWriteScope]
    queryset = User.objects.all()
    serializer_class = UserSerializer


class InventoryCurrentUser(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, TokenHasReadWriteScope]
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

