from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.response import Response
from inventory_requests.serializers.DisburseSerializer import DisburseSerializer
from items.models import Item
from inventory_logger.utility.logger import LoggerUtility

@api_view(['POST'])
def DisburseDirectly(request):

    serializer = DisburseSerializer(data=request.data)
    if serializer.is_valid():
        item = Item.objects.get(pk=serializer.data.get('item_id'))
        try:
            item.quantity = item.quantity - serializer.data.get('quantity')
            item.save()
            #LoggerUtility.log(request.user.username, "DISBURSED", "Disbursed " + item.quantity + " " + item.name)
            return Response(serializer.data)
        except:
            raise MethodNotAllowed(DisburseDirectly, "Cannot disburse the given quantity")
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
