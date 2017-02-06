from oauth2_provider.ext.rest_framework import TokenHasReadWriteScope
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from inventory_requests.serializers.DisburseSerializer import DisburseSerializer
from items.models import Item
from inventory_logger.utility.logger import LoggerUtility
from inventory_logger.action_enum import ActionEnum


@api_view(['POST'])
@permission_classes((TokenHasReadWriteScope, IsAdminUser))
def DisburseDirectly(request):
    serializer = DisburseSerializer(data=request.data)
    if serializer.is_valid():
        item = Item.objects.get(pk=serializer.data.get('item_id'))
        try:
            item.quantity = item.quantity - serializer.data.get('quantity')
            LoggerUtility.log_as_system(ActionEnum.DISBURSED, "Disbursed " + str(item.quantity) + " " + item.name)
            item.save()
            return Response(serializer.data)
        except:
            raise MethodNotAllowed(DisburseDirectly, "Cannot disburse the given quantity")
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)