from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import ParseError, ValidationError

from inventoryProject.utility.print_functions import serializer_pretty_print
from inventory_transaction_logger.action_enum import ActionEnum
from inventory_transaction_logger.utility.logger import LoggerUtility
from items.logic.asset_logic import create_asset_helper
from items.models.asset_custom_fields import IntAssetField, FloatAssetField, ShortTextAssetField, LongTextAssetField, \
    AssetField
from items.models.asset_models import ASSET_HEADERS, Asset
from items.models.item_models import Item
from items.serializers.asset_field_serializer import LongTextAssetFieldSerializer, ShortTextAssetFieldSerializer, \
    FloatAssetFieldSerializer, IntAssetFieldSerializer
from items.serializers.asset_serializer import AssetSerializer

ASSET_FIELD_SERIALIZERS = {'int': IntAssetFieldSerializer,
                           'float': FloatAssetFieldSerializer,
                           'short_text': ShortTextAssetFieldSerializer,
                           'long_text': LongTextAssetFieldSerializer}

ASSET_FIELD_MAP = {'int': IntAssetField,
                   'float': FloatAssetField,
                   'short_text': ShortTextAssetField,
                   'long_text': LongTextAssetField}


def validate_guaranteed_headers(headers, required_headers):
    not_included_header = set()
    for required_header in required_headers:
        if required_header not in headers:
            not_included_header.add(required_header)
    return not_included_header


def validate_headers(headers):
    if len(headers) != len(set(headers)):
        raise ParseError(detail="A valid CSV file cannot contain duplicated headers")
    not_included_header = validate_guaranteed_headers(set(headers), set(ASSET_HEADERS))
    if not_included_header:
        raise ParseError(detail=str(not_included_header) + " are required but not included")
    custom_field_headers = AssetField.objects.values_list('name', flat=True)[::1] if \
        AssetField.objects.exists() else []
    supported_headers = custom_field_headers + ASSET_HEADERS
    difference_headers = set(headers).difference(supported_headers)
    if difference_headers:
        raise ParseError(detail=str(difference_headers) + " are not supported")


def create_asset_csv(item_name, asset_tag=None):
    try:
        item = Item.objects.get(name=item_name)
        if not item.is_asset:
            raise ValidationError(detail='{item_name} is not an asset'.format(item_name=item_name))
        asset = create_asset_helper(item=item)
        if asset_tag:
            if Asset.objects.filter(asset_tag=asset_tag).exists():
                raise ValidationError(detail='asset_tag {tag} must be unique'.format(tag=asset_tag))
            asset.asset_tag = asset_tag
            asset.save()
        item.quantity = item.quantity + 1
        item.save()
    except ObjectDoesNotExist:
        raise ValidationError(detail='Item does not Exist')
    return asset


def add_custom_fields(asset, header, value):
    if not value:
        return None
    field = AssetField.objects.get(name=header)
    detailed_field = ASSET_FIELD_MAP.get(field.type).objects.get(field=field, asset=asset)
    serializer = ASSET_FIELD_SERIALIZERS.get(field.type)(detailed_field, data={'value': value}, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return serializer.instance


def create_and_validate_data(data, headers, user):
    error = []
    try:
        asset = create_asset_csv(item_name=data['item_name'], asset_tag=data.get('asset_tag'))
        comment = serializer_pretty_print(serializer=AssetSerializer(asset),
                                          title=ActionEnum.ADDITIONAL_ITEM_INSTANCES.value, validated=False)
        LoggerUtility.log(initiating_user=user, nature_enum=ActionEnum.ITEM_CREATED,
                          comment=comment, items_affected=[asset.item])
    except ValidationError as e:
        if type(e.detail) is list:
            return [{'detail': e.detail[0]}]
        return [{key: e.detail[key][0]} for key in e.detail]
    custom_field_headers = set(headers).difference(set(ASSET_HEADERS))
    for header in custom_field_headers:
        try:
            add_custom_fields(asset, header, data[header])
        except ValidationError as e:
            error.append({header: e.detail['value'][0]})
    return error







