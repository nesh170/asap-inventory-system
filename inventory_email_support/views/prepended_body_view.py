from rest_framework import generics
from rest_framework import status
from rest_framework.views import APIView

from inventoryProject.permissions import IsStaffUser
from inventory_email_support.models import PrependedBody
from inventory_email_support.serializers.email_serializer import PrependedBodySerializer
from rest_framework.response import Response


class GetPrependedBody(APIView):
    permission_classes = [IsStaffUser]

    def get(self, request, format=None):
        prepended_body = PrependedBody.objects.first()
        serializer = PrependedBodySerializer(prepended_body, many=False)
        return Response(serializer.data)


class ModifyPrependedBody(APIView):
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
