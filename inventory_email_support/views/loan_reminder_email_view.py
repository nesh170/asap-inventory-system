from rest_framework import generics
from rest_framework import status
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.views import APIView

from inventoryProject.permissions import IsStaffUser
from inventory_email_support.models import LoanReminderSchedule
from rest_framework.response import Response
from inventory_email_support.serializers.email_serializer import LoanReminderScheduleSerializer
from datetime import datetime, date


def dates_valid(date_array):
    for date_obj in date_array:
        time_string = date_obj.get('date')
        date_scheduled = datetime.strptime(time_string, "%Y-%m-%d").date()
        if date_scheduled < date.today():
            return False
    return True

def construct_date_objects(date_array):
    for date_obj in date_array:
        time_string = date_obj.get('date')
        date_scheduled = datetime.strptime(time_string, "%Y-%m-%d").date()


class GetLoanReminderDates(generics.ListAPIView):
    permission_classes = [IsStaffUser]
    serializer_class = LoanReminderScheduleSerializer

    def get_queryset(self):
        return LoanReminderSchedule.objects.filter(date__gte=date.today(), executed=False)


class CreateLoanReminderDates(APIView):
    permission_classes = [IsStaffUser]

    def post(self, request, format=None):
        date_array = request.data
        if not dates_valid(date_array=date_array):
            raise MethodNotAllowed(self.post, detail="Cannot send an email on a date that has already passed")
        loan_reminder_dates_delete = LoanReminderSchedule.objects.filter(date__gte=date.today(), executed=False).delete()
        serializer = LoanReminderScheduleSerializer(data=request.data, many=True)
        # will catch an error if try to put in two of the same date
        serializer.is_valid(raise_exception=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
