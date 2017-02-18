import requests
from django.contrib.auth.models import User
from oauth2_provider.ext.rest_framework import TokenHasReadWriteScope
from rest_framework import filters
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.exceptions import ParseError
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from inventoryProject.permissions import IsAdminOrReadOnly
from inventory_user.serializers.user_serializer import UserSerializer, LargeUserSerializer
from items.custom_pagination import LargeResultsSetPagination

from django.conf import settings
import json


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


@api_view(['POST'])
def get_duke_access_token(request):
    if request.method == 'POST':
        code = request.data.get('code')
        redirect_uri = request.data.get('redirect_uri')
        if code is None or redirect_uri is None:
            raise ParseError(detail='Require code and redirect_uri in body')
        data = {
            'grant_type': 'authorization_code',
            'client_id': settings.SOCIAL_AUTH_DUKE_KEY,
            'client_secret': settings.SOCIAL_AUTH_DUKE_SECRET,
            'code': code,
            'redirect_uri': redirect_uri
        }
        response = requests.post(url='https://oauth.oit.duke.edu/oauth/token', data=data)
        return Response(data=response.json())




