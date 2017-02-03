from django.test import TestCase
from rest_framework.exceptions import ParseError

from items.logic.filter_item_logic import FilterItemLogic
from items.models import Item


class FilterItemTestCase(TestCase):
    def setUp(self):
        item = Item.objects.create(name="Fitness Tracker", quantity=5)
        item.tags.create(tag='polar')
        item.tags.create(tag='bear')

        item = Item.objects.create(name="Oscilloscope", quantity=5)
        item.tags.create(tag='polar')
        item.tags.create(tag='king')

        item = Item.objects.create(name="Patrick", quantity=5)
        item.tags.create(tag='Star')
        item.tags.create(tag='Terry')
        item.tags.create(tag='bear')

        self.filter_logic = FilterItemLogic()

    def test_included_item(self):
        filter_item = self.filter_logic.filter_logic('polar,bear', None, None)
        self.assertEqual(filter_item.get(name="Fitness Tracker").name, 'Fitness Tracker')

    def test_excluded_item(self):
        filter_item = self.filter_logic.filter_logic(None, 'Terry,bear', None)
        self.assertEqual(filter_item.get(name="Oscilloscope").name, 'Oscilloscope')

    def test_included_and_excluded_item(self):
        filter_item = self.filter_logic.filter_logic('polar', 'king', 'AND')
        self.assertEqual(filter_item.get(name="Fitness Tracker").name, 'Fitness Tracker')

    def test_included_or_excluded_item(self):
        filter_item = self.filter_logic.filter_logic('polar,bear', 'power,bear', 'OR')
        self.assertEqual(filter_item.get(name="Oscilloscope").name, 'Oscilloscope')
        self.assertEqual(filter_item.get(name="Fitness Tracker").name, 'Fitness Tracker')

    def test_no_operator_error(self):
        successError = False
        try:
            filter_item = self.filter_logic.filter_logic('polar,bear', 'power,bear', None)
        except ParseError:
            successError = True
        self.assertEqual(successError, True)



