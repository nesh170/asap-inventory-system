from django.contrib import admin

from items.models.asset_custom_fields import LongTextAssetField, ShortTextAssetField, FloatAssetField, IntAssetField, \
    AssetField
from items.models.asset_models import Asset
from items.models.item_models import Item, Tag
from items.models.custom_field_models import Field, IntField, FloatField, ShortTextField, LongTextField

# Register your models here.
admin.site.register(Item)
admin.site.register(Tag)
admin.site.register(Field)
admin.site.register(IntField)
admin.site.register(FloatField)
admin.site.register(ShortTextField)
admin.site.register(LongTextField)
admin.site.register(Asset)
admin.site.register(AssetField)
admin.site.register(IntAssetField)
admin.site.register(FloatAssetField)
admin.site.register(ShortTextAssetField)
admin.site.register(LongTextAssetField)