from oauth2_provider.ext.rest_framework import TokenHasReadWriteScope
from rest_framework import generics

from inventory_shopping_cart_request.models import RequestTable
from inventory_requests.serializers.RequestSerializer import RequestSerializer


class ShoppingCartRequestList(generics.ListCreateAPIView):
    permission_classes = [TokenHasReadWriteScope]
    serializer_class = RequestSerializer
    queryset = RequestTable.objects.all()