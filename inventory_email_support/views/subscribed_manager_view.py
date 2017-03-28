from rest_framework import generics
from rest_framework import status
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.views import APIView

from inventoryProject.permissions import IsStaffUser, IsSuperUser
from inventoryProject.utility.queryset_functions import get_or_not_found
from inventory_email_support.models import SubscribedManagers
from rest_framework.response import Response
from inventory_email_support.serializers.email_serializer import SubscribedManagerSerializer


class SubscribedManagerList(generics.ListAPIView):
    permission_classes = [IsSuperUser]
    serializer_class = SubscribedManagerSerializer
    queryset = SubscribedManagers.objects.all()


class Subscribe(APIView):
    permission_classes = [IsStaffUser]

    def post(self, request, format=None):
        user = self.request.user
        if SubscribedManagers.objects.filter(member=user).exists():
            raise MethodNotAllowed(self.post, detail="Already subscribed to the list")
        subscribed_manager = SubscribedManagers.objects.create(member=user)
        return Response(data=SubscribedManagerSerializer(subscribed_manager).data, status=status.HTTP_200_OK)


class CurrentSubscribeUser(APIView):
    permission_classes = [IsStaffUser]

    def get(self, request, *args, **kwargs):
        member_data = get_or_not_found(SubscribedManagers, member=request.user)
        return Response(SubscribedManagerSerializer(member_data).data, status=status.HTTP_200_OK)


class Unsubscribe(APIView):
    permission_classes = [IsStaffUser]

    def post(self, request, format=None):
        user = self.request.user
        if SubscribedManagers.objects.filter(member=user).exists():
            SubscribedManagers.objects.get(member=user).delete()
            return Response(status=status.HTTP_200_OK)
        else:
            raise MethodNotAllowed(self.post, detail="User is not currently subscribed to the manager list")