import csv

from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from rest_framework import status
from rest_framework.decorators import renderer_classes, api_view, permission_classes
from rest_framework.exceptions import ParseError
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView

from inventoryProject.permissions import IsStaffUser
from items.logic.csv_logic import validate_headers, create_and_validate_data, FIELD_MAP
from items.models.item_models import Item, Tag
from items.models.custom_field_models import Field
from items.renderers import ItemRendererCSV


def create_content(item, fields):
    tags = ','.join(Tag.objects.filter(item=item).values_list('tag', flat=True))
    content_dictionary = {'name': item.name, 'quantity': item.quantity, 'model_number': item.model_number,
                          'description': item.description, 'tags': tags, 'is_asset': item.is_asset,
                          'minimum_stock': item.minimum_stock, 'track_minimum_stock': item.track_minimum_stock}
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


@api_view(['GET'])
@renderer_classes((ItemRendererCSV,))
@permission_classes((IsStaffUser,))
def export_example_item_view(request):
    response = Response(data=[], status=status.HTTP_200_OK, content_type='text/csv')
    response['content-disposition'] = 'attachment; filename="field.csv"'
    return response


class ItemCsvImport(APIView):
    parser_classes = (MultiPartParser, FormParser,)

    @transaction.atomic
    def post(self, request, format=None):
        sid = transaction.savepoint()
        error = {}
        my_file = request.FILES['csv_file'] if 'csv_file' in request.FILES else None
        if my_file is None:
            raise ParseError(detail="You need to add a CSV file")
        filename = 'items.csv'
        with open(filename, 'wb+') as temp_file:
            for chunk in my_file.chunks():
                temp_file.write(chunk)
        with open(filename) as csvfile:
            try:
                dialect = csv.Sniffer().sniff(csvfile.readline())
                csvfile.seek(0)
                reader = csv.DictReader(f=csvfile, dialect=dialect)
                validate_headers(reader.fieldnames)
            except UnicodeDecodeError:
                raise ParseError(detail='This is not a valid CSV file, sorry')
            # except csv.Error:
            #     raise ParseError(detail="This csv file is not valid")
            current_row_index = 1
            for row in reader:
                error_list = create_and_validate_data(row, reader.fieldnames, request.user)
                if error_list:
                    error[current_row_index] = error_list
                current_row_index += 1
        if error == {}:
            transaction.savepoint_commit(sid=sid)
            return Response(status=status.HTTP_201_CREATED)
        transaction.savepoint_rollback(sid=sid)
        return Response(data=error, status=status.HTTP_400_BAD_REQUEST)
