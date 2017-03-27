from django.db.models import Q
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from inventory_requests.models import RequestCart
from inventory_requests.serializers.RequestCartSerializer import RequestCartSerializer
from rest_framework import filters


class RequestCartList(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RequestCartSerializer
    filter_backends = (filters.SearchFilter, filters.DjangoFilterBackend)
    filter_fields = ('status', 'cart_disbursements__item__name', )
    search_fields = ('owner__username', 'reason', 'cart_disbursements__item__name', 'cart_loans__item__name')

    def get_queryset(self):
        user = self.request.user
        base_queryset = RequestCart.objects.exclude(Q(status="cancelled") and Q(status="active"))
        return base_queryset if user.is_staff else base_queryset.filter(owner=user)
