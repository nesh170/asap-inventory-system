from oauth2_provider.ext.rest_framework import TokenHasReadWriteScope
from rest_framework import generics
from rest_framework.exceptions import ValidationError

from inventoryProject.permissions import IsAdminOrReadOnly
from inventory_disbursements.models import Disbursement
from inventory_disbursements.serializers.disbursement_serializer import DisbursementSerializer
from items.models import Item


class DisbursementList(generics.ListCreateAPIView):
    permission_classes = [IsAdminOrReadOnly, TokenHasReadWriteScope]
    serializer_class = DisbursementSerializer

    def get_queryset(self):
        return Disbursement.objects.all() if self.request.user.is_staff else \
            Disbursement.objects.filter(receiver=self.request.user)

    def perform_create(self, serializer):
        quantity = serializer.validated_data.get('quantity')
        item_id = serializer.validated_data.get('item_id')
        item = Item.objects.get(id=item_id)
        if quantity > item.quantity:
            error_message = '{quantity} is greater than {name} available, {item_quantity}'.format
            raise ValidationError(detail=error_message(quantity=quantity,name=item.name,item_quantity=item.quantity))
        serializer.save()
        item.quantity = item.quantity - quantity
        item.save()

