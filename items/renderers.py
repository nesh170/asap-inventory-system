from rest_framework_csv.renderers import CSVRenderer

from items.models import Field


class ItemRendererCSV(CSVRenderer):
    custom_fields_header = Field.objects.values_list('name', flat=True)[::1]
    header = ['name', 'quantity', 'description', 'model_number', 'tags'] + custom_fields_header

