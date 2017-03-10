from rest_framework import status
from rest_framework.decorators import renderer_classes, api_view, permission_classes
from rest_framework.response import Response

from inventoryProject.permissions import IsStaffUser
from items.models import Item, Field, Tag, LongTextField, ShortTextField, FloatField, IntField
from items.renderers import ItemRendererCSV

FIELD_MAP = {'int': IntField,
             'float': FloatField,
             'short_text': ShortTextField,
             'long_text': LongTextField}


def create_content(item, fields):
    tags = ','.join(Tag.objects.filter(item=item).values_list('tag',flat=True))
    content_dictionary = {'name': item.name, 'quantity': item.quantity, 'model_number': item.model_number,
                          'description': item.description, 'tags': tags}
    for field in fields:
        table = FIELD_MAP.get(field.type)
        content_dictionary[field.name] = table.objects.get(field=field, item=item).value
    return content_dictionary


@api_view(['GET'])
@renderer_classes((ItemRendererCSV,))
@permission_classes((IsStaffUser,))
def export_item_view(request):
    items = Item.objects.all()
    field_list = Field.objects.all()
    content = [create_content(item, field_list) for item in items]
    response = Response(data=content, status=status.HTTP_200_OK, content_type='text/csv')
    response['content-disposition'] = 'attachment; filename="items.csv"'
    return response
