from rest_framework.exceptions import ParseError

from items.models import Item


class FilterItemLogic:
    def included_item_logic(self, tag_list_included):
        items = Item.objects.filter(tags__tag__in=tag_list_included).distinct()
        for tag in tag_list_included:
            items = items.filter(tags__tag=tag)
        return items

    def excluded_item_logic(self, tag_list_excluded):
        items = Item.objects.exclude(tags__tag__in=tag_list_excluded).distinct()
        for tag in tag_list_excluded:
            items = items.exclude(tags__tag=tag)
        return items

    def operation_item_logic(self, included_item, excluded_item, operation):
        return included_item & excluded_item if operation.upper() == 'AND' else included_item | excluded_item

    def filter_logic(self, tag_included, tag_excluded, operation):
        if tag_included is not None and tag_excluded is None:
            return self.included_item_logic(tag_included.split(','))
        elif tag_excluded is not None and tag_included is None:
            return self.excluded_item_logic(tag_excluded.split(','))
        elif tag_included is not None and tag_excluded is not None:
            if operation is not None:
                return self.operation_item_logic(self.included_item_logic(tag_included.split(',')),
                                                 self.excluded_item_logic(tag_excluded.split(',')),
                                                 operation)
            raise ParseError('You cannot have included tags and excluded tags with no operation, NOOBZ')
        return Item.objects.all()

