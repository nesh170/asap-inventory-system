import requests
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import filters
from rest_framework import generics
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import ParseError
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from inventoryProject.permissions import IsAdminOrReadOnly
from inventory_user.serializers.user_serializer import UserSerializer, LargeUserSerializer
from items.custom_pagination import LargeResultsSetPagination


class InventoryUserList(generics.ListCreateAPIView):
    permission_classes = [IsAdminUser]
    queryset = User.objects.all()
    serializer_class = UserSerializer


class InventoryUser(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser]
    queryset = User.objects.all()
    serializer_class = UserSerializer


class InventoryCurrentUser(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class LargeUserList(generics.ListAPIView):
    permission_classes = [IsAdminUser]
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
        return Response(data=response.json(), status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAdminOrReadOnly])
def get_api_token(request):
    try:
        token = Token.objects.get(user=request.user)
    except ObjectDoesNotExist:
        token = Token.objects.create(user=request.user)
    return Response(data={'token': token.key}, status=status.HTTP_200_OK)





