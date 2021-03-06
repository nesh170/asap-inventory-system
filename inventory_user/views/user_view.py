import requests
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import filters
from rest_framework import generics
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view
from rest_framework.exceptions import ParseError, MethodNotAllowed, NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from inventoryProject.permissions import IsStaffUser, IsSuperUser, IsSuperUserDelete, IsSuperUserOrStaffReadOnly
from inventoryProject.utility.queryset_functions import get_or_not_found, get_or_none
from inventory_email_support.models import SubscribedManagers
from inventory_user.serializers.user_serializer import UserSerializer, LargeUserSerializer
from items.custom_pagination import LargeResultsSetPagination

MEMBER_LIST = [SubscribedManagers]


class InventoryUserList(generics.ListCreateAPIView):
    permission_classes = [IsSuperUserOrStaffReadOnly]
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        if request.data.get('username') is not None:
            user = get_or_none(User, username=request.data.get('username'))
            if user is not None and not user.is_active:
                raise MethodNotAllowed(method=self.post,
                                       detail="An inactive user with this username, {user} already exists."
                                       .format(user=user.username))
        return self.create(request, *args, **kwargs)


class InventoryUser(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsSuperUser, IsSuperUserDelete]
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer

    def perform_update(self, serializer):
        data = serializer.validated_data
        if data.get("is_superuser") is None and data.get("is_staff") is None:
            serializer.save()
        else:
            is_superuser = data.get("is_superuser")
            is_staff = data.get("is_staff")
            if (is_superuser is None or is_staff is None) or (is_superuser and not is_staff):
                raise MethodNotAllowed(detail="Both is_superuser and is_staff has to be true if is_superuser is true"
                                              " and they both have to be included",
                                       method=self.patch)
            serializer.save()

    def perform_destroy(self, instance):
        instance.is_active = False
        for model in MEMBER_LIST:
            member = get_or_none(model, member=instance)
            if member:
                member.delete()
        instance.save()


class InventoryCurrentUser(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer

    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class LargeUserList(generics.ListAPIView):
    permission_classes = [IsStaffUser]
    queryset = User.objects.filter(is_active=True).values('id', 'username').distinct()
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


class ApiToken(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            token = Token.objects.get(user=request.user)
        except ObjectDoesNotExist:
            token = Token.objects.create(user=request.user)
        return Response(data={'token': token.key}, status=status.HTTP_200_OK)

    def delete(self, request):
        token = get_or_not_found(Token, user=request.user)
        token.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)









