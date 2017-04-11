import csv

from django.db import transaction
from rest_framework import status
from rest_framework.decorators import renderer_classes, api_view, permission_classes
from rest_framework.exceptions import ParseError
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView

from inventoryProject.permissions import IsStaffUser
from items.logic.asset_csv_logic import ASSET_FIELD_MAP
from items.logic.asset_csv_logic import validate_headers, create_and_validate_data
from items.models.asset_custom_fields import AssetField
from items.models.asset_models import Asset
from items.models.item_models import Item
from items.renderers import AssetRendererCSV


def create_content(asset, fields):
    content_dictionary = {'item_name': asset.item.name, 'asset_tag': asset.asset_tag}
    for field in fields:
        table = ASSET_FIELD_MAP.get(field.type)
        content_dictionary[field.name] = table.objects.get(field=field, asset=asset).value
    return content_dictionary


@api_view(['GET'])
@renderer_classes((AssetRendererCSV,))
@permission_classes((IsStaffUser,))
def export_asset_view(request):
    item_id = request.GET.get('item_id')
    assets = Asset.objects.filter(item_id=item_id) if item_id else Asset.objects.all()
    field_list = AssetField.objects.all()
    content = [create_content(asset, field_list) for asset in assets]
    response = Response(data=content, status=status.HTTP_200_OK, content_type='text/csv')
    response['content-disposition'] = 'attachment; filename="assets.csv"'
    return response


@api_view(['GET'])
@renderer_classes((AssetRendererCSV,))
@permission_classes((IsStaffUser,))
def export_example_asset_view(request):
    response = Response(data=[], status=status.HTTP_200_OK, content_type='text/csv')
    response['content-disposition'] = 'attachment; filename="field.csv"'
    return response


class AssetCsvImport(APIView):
    parser_classes = (MultiPartParser, FormParser,)

    @transaction.atomic
    def post(self, request, format=None):
        sid = transaction.savepoint()
        error = {}
        my_file = request.FILES['csv_file'] if 'csv_file' in request.FILES else None
        if my_file is None:
            raise ParseError(detail="You need to add a CSV file")
        filename = 'assets.csv'
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
