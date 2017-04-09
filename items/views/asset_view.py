from django.db.models import Q
from rest_framework import generics, filters

from inventoryProject.permissions import IsStaffUser
from inventory_transaction_logger.action_enum import ActionEnum
from inventory_transaction_logger.utility.logger import LoggerUtility
from items.models.asset_models import Asset
from items.serializers.asset_serializer import AssetSerializer
from items.serializers.detailed_asset_serializer import DetailedAssetSerializer


class AssetList(generics.ListCreateAPIView):
    permission_classes = [IsStaffUser]
    serializer_class = AssetSerializer
    filter_backends = (filters.SearchFilter, filters.DjangoFilterBackend)
    filter_fields = ('item__id', )
    search_fields = ('asset_tag', )

    def get_queryset(self):
        available = self.request.GET.get('available')
        if available:
            available_bool = available.lower() == 'true'
            filter_logic = Q(loan__isnull=True) & Q(disbursement__isnull=True) if available_bool else\
                Q(loan__isnull=False) | Q(disbursement__isnull=False)
            return Asset.objects.filter(filter_logic)
        return Asset.objects.all()

    def perform_create(self, serializer):
        serializer.save()
        item = serializer.instance.item
        item.quantity = item.quantity + 1
        item.save()


class AssetDetail(generics.RetrieveUpdateDestroyAPIView):
    # can be used to update the loans in the asset
    permission_classes = [IsStaffUser]
    queryset = Asset.objects.all()
    serializer_class = DetailedAssetSerializer

    def delete(self, request, *args, **kwargs):
        item = self.get_object().item
        comment = "Asset Deleted for item name: {item_name} ; {comment}"\
            .format(item_name=item.name, comment=request.data.get('comment') if request.data.get('comment') else '')
        response = self.destroy(request, *args, **kwargs)
        LoggerUtility.log(initiating_user=request.user, nature_enum=ActionEnum.DESTRUCTION_ITEM_INSTANCES,
                          comment=comment, items_affected=[item])
        return response

    def perform_destroy(self, instance):
        item = instance.item
        item.quantity = item.quantity - 1
        item.save()
        instance.delete()







