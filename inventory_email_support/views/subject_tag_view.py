from rest_framework.views import APIView

from inventoryProject.permissions import IsSuperUser
from inventory_email_support.models import SubjectTag
from inventory_email_support.serializers.email_serializer import SubjectTagSerializer
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response


class GetSubjectTag(generics.ListAPIView):
    permission_classes = [IsSuperUser]
    serializer_class = SubjectTagSerializer
    pagination_class = None
    #TODO fix this, originally had first() but then was getting an error saying SubjectTag has no len(). theoretically,
    # this shouldn't break
    queryset = SubjectTag.objects.all()


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
