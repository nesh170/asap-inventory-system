from django.db import IntegrityError
from rest_framework.exceptions import ValidationError

from inventoryProject.utility.generator_functions import generate_unique_key
from inventory_requests.models import Loan
from items.models.asset_models import Asset, ASSET_TAG_MAX_LENGTH


def add_to_dict_if_not_none(dictionary, key, value):
    if value:
        dictionary[key] = value
    return value is not None


def create_asset_helper(item, loan=None, disbursement=None):
    args = {'item': item}
    if loan and disbursement:
        raise ValidationError(detail='An asset cannot contain both loan and disbursement')
    add_to_dict_if_not_none(args, 'loan', loan)
    add_to_dict_if_not_none(args, 'disbursement', disbursement)
    created = False
    while not created:
        try:
            Asset.objects.create(asset_tag=generate_unique_key(length=ASSET_TAG_MAX_LENGTH, prepend=item.id), **args)
            created = True
        except IntegrityError:
            created = False


def create_assets(item):
    if not Asset.objects.filter(item=item).exists():
        # if there are no assets for the item, create items with assets
        [create_asset_helper(item=item) for x in range(item.quantity)]
        [create_asset_helper(item=item, loan=loan) for loan in
         Loan.objects.filter(item=item, cart__status__in=['approved', 'fulfilled'], returned_timestamp__isnull=False)]

