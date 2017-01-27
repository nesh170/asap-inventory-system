from django.test import TestCase
from items.models import Item


class ItemTestCase(TestCase):
    def setUp(self):
        Item.objects.create(name="quad 2-input NAND gate", quantity=0, model_number="48979", description="Jameco", location="hudson 116")

    def test_search_by_name(self):
        quad_2_input_nand_gate = Item.objects.get(name="quad 2-input NAND gate")
        self.assertEqual(quad_2_input_nand_gate.name,"quad 2-input NAND gate")
