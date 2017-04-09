from django.db.models import Q
from rest_framework import serializers
from rest_framework.exceptions import MethodNotAllowed

from inventory_requests.models import Disbursement, Loan
from inventory_requests.serializers.DisbursementSerializer import DisbursementSerializer, LoanSerializer
from items.models.asset_models import Asset
from items.models.item_models import Item
from items.models.custom_field_models import IntField, FloatField, ShortTextField, LongTextField
from items.serializers.asset_serializer import AssetSerializer
from items.serializers.field_serializer import IntFieldSerializer, FloatFieldSerializer, ShortTextFieldSerializer, \
    LongTextFieldSerializer
from items.serializers.tag_serializer import NestedTagSerializer


def get_values(table, is_staff, item, serializer_constructor):
    field = table.objects.filter(item=item) if is_staff \
        else table.objects.filter(field__private=False, item=item)
    serializer = serializer_constructor(instance=field, many=True)
    return serializer.data


class DetailedItemSerializer(serializers.ModelSerializer):
    tags = NestedTagSerializer(many=True, allow_null=True, required=False)
    int_fields = serializers.SerializerMethodField()
    float_fields = serializers.SerializerMethodField()
    short_text_fields = serializers.SerializerMethodField()
    long_text_fields = serializers.SerializerMethodField()
    outstanding_disbursements = serializers.SerializerMethodField()
    outstanding_loans = serializers.SerializerMethodField()
    current_loans = serializers.SerializerMethodField()

    def get_int_fields(self, obj):
        return get_values(IntField, self.context['request'].user.is_staff, obj, IntFieldSerializer)

    def get_float_fields(self, obj):
        return get_values(FloatField, self.context['request'].user.is_staff, obj, FloatFieldSerializer)

    def get_short_text_fields(self, obj):
        return get_values(ShortTextField, self.context['request'].user.is_staff, obj, ShortTextFieldSerializer)

    def get_long_text_fields(self, obj):
        return get_values(LongTextField, self.context['request'].user.is_staff, obj, LongTextFieldSerializer)

    def get_outstanding_disbursements(self, obj):
        user = self.context['request'].user
        q_func = Q(cart__status='outstanding', item=obj)
        q_func = q_func if user.is_staff else q_func & Q(cart__owner=user)
        return DisbursementSerializer(Disbursement.objects.filter(q_func), many=True).data

    def get_outstanding_loans(self, obj):
        user = self.context['request'].user
        q_func = Q(cart__status='outstanding', item=obj)
        q_func = q_func if user.is_staff else q_func & Q(cart__owner=user)
        return LoanSerializer(Loan.objects.filter(q_func), many=True).data

    def get_current_loans(self, obj):
        user = self.context['request'].user
        q_func = Q(cart__status='fulfilled', item=obj, returned_timestamp__isnull=True)
        q_func = q_func if user.is_staff else q_func & Q(cart__owner=user)
        return LoanSerializer(Loan.objects.filter(q_func), many=True).data

    class Meta:
        model = Item
        fields = ('id', 'name', 'quantity', 'model_number', 'description', 'tags', 'int_fields', 'float_fields',
                  'short_text_fields', 'long_text_fields', 'outstanding_disbursements', 'outstanding_loans',
                  'current_loans', 'minimum_stock', 'track_minimum_stock', 'is_asset')

    def update(self, instance, validated_data):
        if instance.is_asset:
            if validated_data.get('is_asset') is not None and not validated_data.get('is_asset'):
                raise MethodNotAllowed(method=self.update, detail='This Item is already an Asset')
            if validated_data.get('quantity') is not None:
                raise MethodNotAllowed(method=self.update, detail='Cannot change quantity if Item is an Asset')
        instance.name = validated_data.get('name', instance.name)
        instance.quantity = validated_data.get('quantity', instance.quantity)
        instance.model_number = validated_data.get('model_number', instance.model_number)
        instance.description = validated_data.get('description', instance.description)
        instance.minimum_stock = validated_data.get('minimum_stock', instance.minimum_stock)
        instance.track_minimum_stock = validated_data.get('track_minimum_stock', instance.track_minimum_stock)
        instance.is_asset = validated_data.get('is_asset', instance.is_asset)
        instance.save()
        return instance
