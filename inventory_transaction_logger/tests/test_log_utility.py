from django.contrib.auth.models import User
from django.test import TestCase

from inventory_disbursements.models import Cart
from inventory_shopping_cart.models import ShoppingCart
from inventory_transaction_logger.action_enum import ActionEnum
from inventory_transaction_logger.models import Log, Action, ItemLog, ShoppingCartLog
from inventory_transaction_logger.utility.logger import LoggerUtility
from items.models import Item

ADMIN_USERNAME = 'test'
ADMIN_PASSWORD = 'testPassword'

USER_USERNAME = 'user'
USER_PASSWORD = 'masalaPassword'


def equal_shopping_cart(test_equal, shopping_cart_log, shopping_cart_affected):
    test_equal.assertEqual(shopping_cart_log.shopping_cart.owner, shopping_cart_affected.owner)
    test_equal.assertEqual(shopping_cart_log.shopping_cart.status, shopping_cart_affected.status)
    test_equal.assertEqual(shopping_cart_log.shopping_cart.reason, shopping_cart_affected.reason)
    test_equal.assertEqual(shopping_cart_log.shopping_cart.admin_comment, shopping_cart_affected.admin_comment)
    test_equal.assertEqual(shopping_cart_log.shopping_cart.admin, shopping_cart_affected.admin)


def equal_item(test_equal, item_log, item_affected):
    test_equal.assertEqual(item_log.item.name, item_affected.name)
    test_equal.assertEqual(item_log.item.quantity, item_affected.quantity)
    test_equal.assertEqual(item_log.item.model_number, item_affected.model_number)
    test_equal.assertEqual(item_log.item.description, item_affected.description)
    if item_log.item.tags is not None:
        item_log_tags = item_log.item.tags.all()
        item_affected_tags = item_affected.tags.all()
        for x in range(0, len(item_log_tags)):
            item_log_tag = item_log_tags[x]
            item_affected_tag = item_affected_tags[x]
            test_equal.assertEqual(item_log_tag, item_affected_tag)


def equal_log(test_equal, log_id, initiating_user, nature_enum, comment, affected_user = None, items_affected = None,
              carts_affected = None, disbursement_affected = None):
    log_entry = Log.objects.get(pk=log_id)
    test_equal.assertEqual(log_entry.initiating_user, initiating_user)
    test_equal.assertEqual(log_entry.nature.tag, nature_enum.value)
    if affected_user is not None:
        test_equal.assertEqual(log_entry.affected_user, affected_user)
    if comment is not None:
        test_equal.assertEqual(log_entry.comment, comment)
    if items_affected is not None:
        item_logs = log_entry.item_log.all()
        for x in range(0, len(item_logs)):
            item_log = item_logs[x]
            item_affected = items_affected[x]
            equal_item(test_equal, item_log, item_affected)
    if carts_affected is not None:
        shopping_cart_logs = log_entry.shopping_cart_log.all()
        for y in range(0, len(shopping_cart_logs)):
            shoppping_cart_log = shopping_cart_logs[y]
            shopping_cart_affected = carts_affected[y]
            equal_shopping_cart(test_equal, shoppping_cart_log, shopping_cart_affected)
    if disbursement_affected is not None:
        updated_disbursement_cart = log_entry.disbursement_log.all()
        test_equal.assertEqual(updated_disbursement_cart.count(), len(disbursement_affected))
        [test_equal.assertEqual(updated_disbursement_cart.get(pk=disburse.id).cart, disburse.cart)
         for disburse in updated_disbursement_cart]


class LogUtilityTestCase(TestCase):
    def setUp(self):

        self.admin = User.objects.create_superuser(ADMIN_USERNAME, 'test@test.com', ADMIN_PASSWORD)
        self.normal_user = User.objects.create_user(USER_USERNAME, 'user@testforlife.com', USER_PASSWORD)
        Action.objects.create(color='1', tag='ITEM CREATED')
        Action.objects.create(color='2', tag='CUSTOM FIELD CREATED')

    def test_utility_item_cart_provided(self):
        item_with_one_tag = Item.objects.create(name="oscilloscope", quantity=3, model_number="48979",
                                                description="oscilloscope")
        item_with_one_tag.tags.create(tag="test")
        item_with_zero_tags = Item.objects.create(name="resistor", quantity=50, model_number="1234", description="resistor")
        items_affected = [item_with_one_tag, item_with_zero_tags]
        shopping_cart = ShoppingCart.objects.create(owner=self.normal_user, status="active", reason="test shopping cart",
                                                               admin_comment="this is an admin comment", admin=self.admin)
        another_shopping_cart = ShoppingCart.objects.create(owner=self.admin, status="outstanding", reason="another shopping cart",
                                                            admin_comment="hi", admin=self.admin)
        shopping_cart_affected = [shopping_cart, another_shopping_cart]
        disbursement_cart = [Cart.objects.create(disburser=self.admin, receiver=self.normal_user, comment="lit")]
        log_entry = LoggerUtility.log(self.admin, ActionEnum.ITEM_CREATED,  'Creating an item', self.normal_user,
                                      items_affected, shopping_cart_affected, disbursement_cart)
        equal_log(self, log_entry.id, self.admin, ActionEnum.ITEM_CREATED, 'Creating an item', self.normal_user,
                  items_affected, shopping_cart_affected, disbursement_cart)

    def test_utility_no_item_cart(self):
        log_entry = LoggerUtility.log(self.admin, ActionEnum.CUSTOM_FIELD_CREATED, 'Creating a custom field', self.normal_user)
        equal_log(self, log_entry.id, self.admin, ActionEnum.CUSTOM_FIELD_CREATED,  'Creating a custom field', self.normal_user)


