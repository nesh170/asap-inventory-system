from datetime import datetime

from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.exceptions import MethodNotAllowed

from inventoryProject.utility.queryset_functions import get_or_not_found
from inventory_requests.models import RequestCart
from items.models.asset_models import Asset


class InstantRequestSerializer(serializers.Serializer):
    current_type = serializers.ChoiceField(choices=['loan', 'disbursement'], required=True)
    asset_id = serializers.IntegerField(min_value=1, required=True)
    owner_id = serializers.IntegerField(min_value=1, required=True)

    def create(self, validated_data):
        owner = get_or_not_found(User, pk=validated_data.get('owner_id'))
        asset = get_or_not_found(Asset, pk=validated_data.get('asset_id'))
        if asset.loan or asset.disbursement:
            raise MethodNotAllowed(method=self.create, detail='Asset is already tied to loan/disbursement')
        cart = RequestCart.objects.create(owner=owner, status='fulfilled', staff_timestamp=datetime.now())
        args = {'item': asset.item, 'quantity': 1}
        if validated_data.get('current_type') == 'loan':
            loan = cart.cart_loans.create(loaned_timestamp=datetime.now(), **args)
            asset.loan = loan
        else:
            disbursement = cart.cart_disbursements.create(**args)
            asset.disbursement = disbursement
        item = asset.item
        item.quantity = item.quantity - 1
        item.save()
        asset.save()
        cart = RequestCart.objects.get(pk=cart.id)
        return cart
