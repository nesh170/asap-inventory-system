from rest_framework_csv.renderers import CSVRenderer

from items.models import Field, ITEM_HEADERS


class ItemRendererCSV(CSVRenderer):
    custom_fields_header = Field.objects.values_list('name', flat=True)[::1] if Field.objects.exists() else []
    header = ITEM_HEADERS + custom_fields_header

