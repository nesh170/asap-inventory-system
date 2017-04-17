from django.db.models import Q
from rest_framework import generics, filters, status
from rest_framework.exceptions import ParseError
from rest_framework.response import Response
from rest_framework.views import APIView

from inventoryProject.permissions import IsStaffUser
from inventoryProject.utility.queryset_functions import get_or_not_found
from inventory_requests.models import Loan, Disbursement
from inventory_requests.serializers.DisbursementSerializer import LoanSerializer, DisbursementSerializer
from inventory_transaction_logger.action_enum import ActionEnum
from inventory_transaction_logger.utility.logger import LoggerUtility
from items.models.asset_models import Asset
from items.serializers.asset_serializer import AssetSerializer
from items.serializers.detailed_asset_serializer import DetailedAssetSerializer


class AssetList(generics.ListCreateAPIView):
    permission_classes = [IsStaffUser]
    serializer_class = AssetSerializer
    filter_backends = (filters.SearchFilter, filters.DjangoFilterBackend)
    filter_fields = ('item__id', 'loan__id', 'disbursement__id')
    search_fields = ('asset_tag', )

    def get_queryset(self):
        available = self.request.GET.get('available')
        loan_id = self.request.GET.get('loan_available_id')
        disbursement_id = self.request.GET.get('disbursement_available_id')
        if available:
            available_bool = available.lower() == 'true'
            filter_logic = Q(loan__isnull=True) & Q(disbursement__isnull=True) if available_bool else\
                Q(loan__isnull=False) | Q(disbursement__isnull=False)
            if loan_id:
                filter_logic = filter_logic | Q(loan__id=loan_id)
            if disbursement_id:
                filter_logic = filter_logic | Q(disbursement__id=disbursement_id)
            return Asset.objects.filter(filter_logic)
        return Asset.objects.all()

    def perform_create(self, serializer):
        serializer.save()
        item = serializer.instance.item
        item.quantity = item.quantity + 1
        item.save()
        comment = "Asset {tag} Created for item name: {item_name}".format(item_name=item.name,
                                                                          tag=serializer.instance.asset_tag)
        LoggerUtility.log(initiating_user=self.request.user, nature_enum=ActionEnum.ADDITIONAL_ITEM_INSTANCES,
                          comment=comment, items_affected=[item])


class AssetDetail(generics.RetrieveUpdateDestroyAPIView):
    # can be used to update the loans in the asset
    permission_classes = [IsStaffUser]
    queryset = Asset.objects.all()
    serializer_class = DetailedAssetSerializer

    def delete(self, request, *args, **kwargs):
        item = self.get_object().item
        asset_tag = self.get_object().asset_tag
        comment = "Asset {tag} Deleted for item name: {item_name} ; {comment}"\
            .format(item_name=item.name, comment=request.data.get('comment') if request.data.get('comment') else '',
                    tag=asset_tag)
        response = self.destroy(request, *args, **kwargs)
        LoggerUtility.log(initiating_user=request.user, nature_enum=ActionEnum.DESTRUCTION_ITEM_INSTANCES,
                          comment=comment, items_affected=[item])
        return response

    def perform_destroy(self, instance):
        item = instance.item
        item.quantity = item.quantity - 1
        item.save()
        instance.delete()


class ClearAssetLoanDisbursement(APIView):
    permission_classes = [IsStaffUser]

    def post(self, request):
        if not request.data.get('id') or not request.data.get('current_type'):
            raise ParseError(detail='Must contain pk and current_type which is loan/disbursement')
        request_type = get_or_not_found(Loan, pk=request.data.get('id')) \
            if request.data.get('current_type').lower() == 'loan' \
            else get_or_not_found(Disbursement, pk=request.data.get('id'))
        for asset in request_type.assets.all():
            asset.loan = None
            asset.disbursement = None
            asset.save()
        serializer_type = LoanSerializer if request.data.get('current_type').lower() == 'loan'\
            else DisbursementSerializer
        return Response(status=status.HTTP_200_OK, data=serializer_type(request_type).data)

