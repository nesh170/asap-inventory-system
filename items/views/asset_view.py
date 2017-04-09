from django.db.models import Q
from rest_framework import generics, filters

from inventoryProject.permissions import IsStaffUser
from items.models.asset_models import Asset
from items.serializers.asset_serializer import AssetSerializer


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
    serializer_class = AssetSerializer

    def delete(self, request, *args, **kwargs):
        comment = request.data.get('comment')
        response = self.destroy(request, *args, **kwargs)
        # TODO: add logger call here
        return response

    def perform_destroy(self, instance):
        item = instance.item
        item.quantity = item.quantity - 1
        item.save()
        instance.delete()







