from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from inventory_requests.models import RequestCart
from inventory_requests.serializers.RequestCartSerializer import RequestCartSerializer
from rest_framework import filters


class RequestCartList(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RequestCartSerializer
    filter_backends = (filters.SearchFilter, filters.DjangoFilterBackend)
    filter_fields = ('status', 'cart_disbursements__item__name', )
    search_fields = ('owner__username', 'reason', 'cart_disbursements__item__name', )

    def get_queryset(self):
        user = self.request.user
        return RequestCart.objects.exclude(status="cancelled").exclude(status="active") if user.is_staff \
            else RequestCart.objects.filter(owner=user).exclude(status="cancelled").exclude(status="active")