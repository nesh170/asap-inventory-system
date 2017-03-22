from rest_framework import generics
from rest_framework import status
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.views import APIView

from inventoryProject.permissions import IsStaffUser, IsSuperUser
from inventory_email.models import SubscribedManagers, SubjectTag
from rest_framework.response import Response
from inventory_email.serializers.subject_tag_serializer import SubjectTagSerializer
from post_office.models import EmailTemplate


class Subscribe(APIView):
    permission_classes = [IsStaffUser]

    def post(self, request, format=None):
        user = self.request.user
        if SubscribedManagers.objects.filter(member=user).exists():
            raise MethodNotAllowed(self.post, detail="Already subscribed to the list")
        SubscribedManagers.objects.create(member=user)
        return Response(status=status.HTTP_200_OK)

class CreateEmailTemplate(APIView):
    def post(self, request, format=None):
        EmailTemplate.objects.create(
            name='request_created',
            subject='{{ subject }}',
            html_content='<p> Hi {{ name }}, </p> <p> Your request was successfully submitted! A staff member will take a '
                 'look at it as soon as possible. </p> <p> Best Regards, <br /> ECE Inventory System Staff </p>'
        )


class Unsubscribe(APIView):
    permission_classes = [IsStaffUser]

    def post(self, request, format=None):
        user = self.request.user
        if SubscribedManagers.objects.filter(member=user).exists():
            SubscribedManagers.objects.get(member=user).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            raise MethodNotAllowed(self.post, detail="User is not currently subscribed to the manager list")


class EditSubjectTag(APIView):
    #TODO this is only dependent on the variance request being approved
    permission_classes = [IsSuperUser]

    def patch(self, request, format=None):
        if SubjectTag.objects.count() == 0:
            SubjectTag.objects.create(subject_tag=request.data)
            return Response(status=status.HTTP_200_OK)
        else:
            subjectTag = SubjectTag.objects.get(pk=1)
            serializer = SubjectTagSerializer(subjectTag, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
