from items.models import Item


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




