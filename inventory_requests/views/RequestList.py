from oauth2_provider.ext.rest_framework import TokenHasReadWriteScope
from rest_framework import filters
from rest_framework import generics

from inventory_requests.models import Request
from inventory_requests.serializers.RequestSerializer import RequestSerializer


class RequestList(generics.ListCreateAPIView):
    permission_classes = [TokenHasReadWriteScope]
    serializer_class = RequestSerializer
    filter_backends = (filters.SearchFilter, filters.DjangoFilterBackend)
    filter_fields = ('owner__username', 'status', 'quantity', 'item__name')
    search_fields = ('owner__username', 'item__name', 'reason')
    def get_queryset(self):
        user = self.request.user
        return Request.objects.exclude(status="cancelled") if user.is_staff \
            else Request.objects.filter(owner=user).exclude(status="cancelled")