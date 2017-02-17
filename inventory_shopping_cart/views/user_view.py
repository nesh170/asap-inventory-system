from django.contrib.auth.models import User
from oauth2_provider.ext.rest_framework import TokenHasReadWriteScope
from rest_framework import filters
from rest_framework import generics
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from inventoryProject.permissions import IsAdminOrReadOnly
from inventory_user.serializers.user_serializer import UserSerializer, LargeUserSerializer
from items.custom_pagination import LargeResultsSetPagination


class InventoryUserList(generics.ListCreateAPIView):
    permission_classes = [IsAdminUser, TokenHasReadWriteScope]
    queryset = User.objects.all()
    serializer_class = UserSerializer


class InventoryUser(generics.RetrieveDestroyAPIView):
    permission_classes = [IsAdminUser, TokenHasReadWriteScope]
    queryset = User.objects.all()
    serializer_class = UserSerializer


class InventoryCurrentUser(generics.RetrieveAPIView):
    permission_classes = [IsAdminOrReadOnly, TokenHasReadWriteScope]
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class LargeUserList(generics.ListAPIView):
    permission_classes = [IsAdminUser, TokenHasReadWriteScope]
    queryset = User.objects.all().values('id', 'username').distinct()
    serializer_class = LargeUserSerializer
    pagination_class = LargeResultsSetPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username', )


