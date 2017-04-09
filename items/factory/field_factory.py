from items.models.asset_models import Asset
from items.models.item_models import Item


class FieldFactory():
    def __init__(self):
        self.factory_dictionary = {
            "int": self.create_int_field,
            "float": self.create_float_field,
            "short_text": self.create_short_text_field,
            "long_text": self.create_long_text_field
        }

    def create_int_field(self, field, item):
        item.int_fields.create(field=field)

    def create_float_field(self, field, item):
        item.float_fields.create(field=field)

    def create_short_text_field(self, field, item):
        item.short_text_fields.create(field=field)

    def create_long_text_field(self, field, item):
        item.long_text_fields.create(field=field)

    def create_field(self, field, item):
        func = self.factory_dictionary.get(field.type)
        func(field=field, item=item)

    def create_field_all_items(self, field):
        [self.create_field(field=field, item=item) for item in Item.objects.all()]


class AssetFieldFactory():
    def __init__(self):
        self.factory_dictionary = {
            "int": self.create_int_asset_field,
            "float": self.create_float_asset_field,
            "short_text": self.create_short_text_asset_field,
            "long_text": self.create_long_text_asset_field
        }

    def create_int_asset_field(self, field, asset):
        asset.int_fields.create(field=field)

    def create_float_asset_field(self, field, asset):
        asset.float_fields.create(field=field)

    def create_short_text_asset_field(self, field, asset):
        asset.short_text_fields.create(field=field)

    def create_long_text_asset_field(self, field, asset):
        asset.long_text_fields.create(field=field)

    def create_asset_field(self, field, asset):
        func = self.factory_dictionary.get(field.type)
        func(field=field, asset=asset)

    def create_asset_field_all_assets(self, field):
        [self.create_asset_field(field=field, asset=asset) for asset in Asset.objects.all()]





