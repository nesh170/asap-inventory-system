from django.db import IntegrityError
from rest_framework.exceptions import ValidationError

from inventoryProject.utility.generator_functions import generate_unique_key
from inventory_requests.models import Loan
from items.factory.field_factory import AssetFieldFactory
from items.models.asset_custom_fields import AssetField
from items.models.asset_models import Asset, ASSET_TAG_MAX_LENGTH


def add_to_dict_if_not_none(dictionary, key, value):
    if value:
        dictionary[key] = value
    return value is not None


def create_asset_fields(asset):
    factory = AssetFieldFactory()
    fields = AssetField.objects.all()
    [factory.create_asset_field(field, asset) for field in fields]


def create_asset_helper(item, loan=None, disbursement=None):
    args = {'item': item}
    if loan and disbursement:
        raise ValidationError(detail='An asset cannot contain both loan and disbursement')
    add_to_dict_if_not_none(args, 'loan', loan)
    add_to_dict_if_not_none(args, 'disbursement', disbursement)
    created = False
    while not created:
        try:
            asset = Asset.objects.create(asset_tag=generate_unique_key(length=ASSET_TAG_MAX_LENGTH, prepend=item.id),
                                         **args)
            created = True
            create_asset_fields(asset)
            return asset
        except IntegrityError:
            created = False
    return None


def create_assets(item):
    # These are currently approved/fulfilled loans which haven't been returned to the staff
    loan_queryset = Loan.objects.filter(item=item, cart__status__in=['approved', 'fulfilled'],
                                        returned_timestamp__isnull=False)
    if not Asset.objects.filter(item=item).exists():
        # if there are no assets for the item, create items with assets
        [create_asset_helper(item=item) for x in range(item.quantity)]
        [create_asset_helper(item=item, loan=loan) for loan in loan_queryset]


