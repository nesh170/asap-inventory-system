from rest_framework_csv.renderers import CSVRenderer

from items.models.asset_custom_fields import AssetField
from items.models.asset_models import ASSET_HEADERS
from items.models.item_models import ITEM_HEADERS
from items.models.custom_field_models import Field


class ItemRendererCSV(CSVRenderer):
    custom_fields_header = Field.objects.values_list('name', flat=True)[::1] if Field.objects.exists() else []
    header = ITEM_HEADERS + custom_fields_header


class AssetRendererCSV(CSVRenderer):
    custom_field_header = AssetField.objects.values_list('name', flat=True)[::1] if AssetField.objects.exists() else []
    header = ASSET_HEADERS + custom_field_header

