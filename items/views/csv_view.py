import csv

from django.db import transaction
from rest_framework import status
from rest_framework.decorators import renderer_classes, api_view, permission_classes
from rest_framework.exceptions import ParseError
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView

from inventoryProject.permissions import IsStaffUser
from items.logic.csv_logic import validate_headers, create_and_validate_data, FIELD_MAP
from items.models import Item, Field, Tag
from items.renderers import ItemRendererCSV


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


class ItemCsvImport(APIView):
    parser_classes = (MultiPartParser, FormParser,)

    @transaction.atomic
    def post(self, request, format=None):
        sid = transaction.savepoint()
        error = {}
        my_file = request.FILES['csv_file']
        filename = 'items.csv'
        with open(filename, 'wb+') as temp_file:
            for chunk in my_file.chunks():
                temp_file.write(chunk)
        with open(filename) as csvfile:
            try:
                dialect = csv.Sniffer().sniff(csvfile.read(1024))
                csvfile.seek(0)
                reader = csv.DictReader(f=csvfile, dialect=dialect)
                validate_headers(reader.fieldnames)
            except UnicodeDecodeError:
                raise ParseError(detail='This is not a valid CSV file, sorry')
            except csv.Error:
                raise ParseError(detail="This csv file is not valid")
            for row in reader:
                error_list = create_and_validate_data(row, reader.fieldnames)
                if error_list:
                    error[row['name']] = error_list
        if error == {}:
            transaction.savepoint_commit(sid=sid)
            return Response(status=status.HTTP_201_CREATED)
        transaction.savepoint_rollback(sid=sid)
        return Response(data=error, status=status.HTTP_400_BAD_REQUEST)
