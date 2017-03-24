from rest_framework import status
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.views import APIView

from inventoryProject.permissions import IsStaffUser, IsSuperUser
from inventory_email_support.models import SubscribedManagers, SubjectTag, PrependedBody
from rest_framework.response import Response
from inventory_email_support.serializers.email_serializer import SubjectTagSerializer, PrependedBodySerializer
from post_office.models import Email
from datetime import datetime

class Subscribe(APIView):
    permission_classes = [IsStaffUser]

    def post(self, request, format=None):
        user = self.request.user
        if SubscribedManagers.objects.filter(member=user).exists():
            raise MethodNotAllowed(self.post, detail="Already subscribed to the list")
        SubscribedManagers.objects.create(member=user)
        return Response(status=status.HTTP_200_OK)


class Unsubscribe(APIView):
    permission_classes = [IsStaffUser]

    def post(self, request, format=None):
        user = self.request.user
        if SubscribedManagers.objects.filter(member=user).exists():
            SubscribedManagers.objects.get(member=user).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            raise MethodNotAllowed(self.post, detail="User is not currently subscribed to the manager list")

# class ConfigureDatesBody(APIView):
#     permission_classes = [IsStaffUser]
#     # go through all dates passed in request. for each date, if date is before datetime.now, then email
#     # has already sent. if not, delete the email from the post_office_email table and create a new one
#     def post(self, request, format=None):
#         date_array = request.data
#         for date_obj in date_array:
#             time_string = date_obj.get('date')
#             date_time_scheduled = datetime.strptime(time_string, "%Y-%m-%dT%H:%M:%S")
#             #TODO consider comparing to just today's date, not time. what if they want to send email out on same day?
#             if date_time_scheduled < datetime.now():
#                 raise MethodNotAllowed(self.post, detail="Cannot send an email on a date before today")
#             # delete all emails from post_office_email table
#             else:
#                 for loan_reminder_email in LoanReminderEmails.objects.all():
#                     if loan_reminder_email.email.scheduled_time >= datetime.now():
#                         Email.objects.get(pk=loan_reminder_email.email.id).delete()
#                         Email.objects.create()
#
#
#
#
        # return Response(status=status.HTTP_200_OK)


class EditSubjectTag(APIView):
    permission_classes = [IsSuperUser]

    def patch(self, request, format=None):
        if SubjectTag.objects.count() == 0:
            serializer = SubjectTagSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            subject_tag = SubjectTag.objects.first()
            serializer = SubjectTagSerializer(subject_tag, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EditPrependedBody(APIView):
    permission_classes = [IsStaffUser]

    def patch(self, request, format=None):
        if PrependedBody.objects.count() == 0:
            serializer = PrependedBodySerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            prepended_body = PrependedBody.objects.first()
            serializer = PrependedBodySerializer(prepended_body, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)