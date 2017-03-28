from rest_framework.exceptions import ParseError, ValidationError

from items.models import ITEM_HEADERS, Field, IntField, FloatField, ShortTextField, LongTextField
from items.serializers.field_serializer import IntFieldSerializer, FloatFieldSerializer, ShortTextFieldSerializer, \
    LongTextFieldSerializer
from items.serializers.item_serializer import ItemSerializer

FIELD_SERIALIZERS = {'int': IntFieldSerializer,
                     'float': FloatFieldSerializer,
                     'short_text': ShortTextFieldSerializer,
                     'long_text': LongTextFieldSerializer}

FIELD_MAP = {'int': IntField,
             'float': FloatField,
             'short_text': ShortTextField,
             'long_text': LongTextField}


def validate_guaranteed_headers(headers, required_headers):
    not_included_header = set()
    for required_header in required_headers:
        if required_header not in headers:
            not_included_header.add(required_header)
    return not_included_header


def validate_headers(headers):
    if len(headers) != len(set(headers)):
        raise ParseError(detail="A valid CSV file cannot contain duplicated headers")
    not_included_header = validate_guaranteed_headers(set(headers), set(ITEM_HEADERS))
    if not_included_header:
        raise ParseError(detail=str(not_included_header) + " are required but not included")
    custom_field_headers = Field.objects.values_list('name', flat=True)[::1] if \
        Field.objects.exists() else []
    supported_headers = custom_field_headers + ITEM_HEADERS
    difference_headers = set(headers).difference(supported_headers)
    if difference_headers:
        raise ParseError(detail=str(difference_headers) + " are not supported")


def create_item(name, quantity, model_number, description, tags):
    data = {'name': name, 'quantity': quantity, 'model_number': model_number, 'description': description}
    if tags:
        data['tags'] = [{'tag': tag} for tag in tags.split(',')]
    serializer = ItemSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    serializer.save()   
    return serializer.instance


def add_custom_fields(item, header, value):
    if not value:
        return None
    field = Field.objects.get(name=header)
    detailed_field = FIELD_MAP.get(field.type).objects.get(field=field, item=item)
    serializer = FIELD_SERIALIZERS.get(field.type)(detailed_field, data={'value': value}, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return serializer.instance


def create_and_validate_data(data, headers):
    error = []
    try:
        item = create_item(data['name'], data['quantity'], data['model_number'], data['description'], data['tags'])
    except ValidationError as e:
        return [{key: e.detail[key][0]} for key in e.detail]
    custom_field_headers = set(headers).difference(set(ITEM_HEADERS))
    for header in custom_field_headers:
        try:
            add_custom_fields(item, header, data[header])
        except ValidationError as e:
            error.append({header: e.detail['value'][0]})
    return error







