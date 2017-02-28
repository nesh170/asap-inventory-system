import django_filters
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.exceptions import NotFound
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from inventory_transaction_logger.models import Log
from inventory_transaction_logger.serializers.log_serializer import LogSerializer


class LogFilter(django_filters.rest_framework.FilterSet):
    min_time = django_filters.IsoDateTimeFilter(name="timestamp", lookup_expr='gte')
    max_time = django_filters.IsoDateTimeFilter(name="timestamp", lookup_expr='lte')

    class Meta:
        model = Log
        fields = ['initiating_user__username', 'nature__tag', 'min_time', 'max_time', 'affected_user__username']


class LogList(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LogSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filter_class = LogFilter
    search_fields = ('initiating_user__username', 'item_log__item__name', 'affected_user__username', )

    def get_queryset(self):
        item_name = self.request.GET.get('item_name')
        if item_name is not None:
            filter_condition = Q(disbursement_log__cart__disbursements__item__name=item_name) \
                     | Q(shopping_cart_log__shopping_cart__requests__item__name=item_name) \
                     | Q(item_log__item__name=item_name)
            return Log.objects.filter(filter_condition)
        return Log.objects.all()


def get_log(pk):
    try:
        return Log.objects.get(pk=pk)
    except Log.DoesNotExist:
        raise NotFound(detail="Log not found")


class ViewDetailedLog(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk, format=None):
        log = get_log(pk)
        serializer = LogSerializer(log)
        return Response(serializer.data)