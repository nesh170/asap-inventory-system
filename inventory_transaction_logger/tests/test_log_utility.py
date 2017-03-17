from django.contrib.auth.models import User
from django.test import TestCase

from inventory_requests.models import RequestCart
from inventory_transaction_logger.action_enum import ActionEnum
from inventory_transaction_logger.models import Log
from inventory_transaction_logger.utility.logger import LoggerUtility
from items.models import Item

ADMIN_USERNAME = 'test'
ADMIN_PASSWORD = 'testPassword'

USER_USERNAME = 'user'
USER_PASSWORD = 'masalaPassword'


def equal_request(test_equal, request_log, request_affected):
    test_equal.assertEqual(request_log.request_cart, request_affected)


def equal_item(test_equal, item_log, item_affected):
    test_equal.assertEqual(item_log.item, item_affected)


def equal_log(test_equal, log_id, initiating_user, nature_enum, comment, affected_user=None, items_affected=None,
              requests_affected=None):
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
    if requests_affected is not None:
        requests_queryset = log_entry.request_cart_log
        test_equal.assertEqual(len(requests_affected), requests_queryset.count())
        [equal_request(test_equal, requests_queryset.get(request_cart__id=request_affected.id), request_affected)
         for request_affected in requests_affected]


class LogUtilityTestCase(TestCase):
    fixtures = ['logger_action.json']

    def setUp(self):
        self.admin = User.objects.create_superuser(ADMIN_USERNAME, 'test@test.com', ADMIN_PASSWORD)
        self.normal_user = User.objects.create_user(USER_USERNAME, 'user@testforlife.com', USER_PASSWORD)

    def test_utility_item_cart_provided(self):
        item_with_one_tag = Item.objects.create(name="oscilloscope", quantity=3, model_number="48979",
                                                description="oscilloscope")
        item_with_one_tag.tags.create(tag="test")
        item_with_zero_tags = Item.objects.create(name="resistor", quantity=50, model_number="1234", description="r")
        items_affected = [item_with_one_tag, item_with_zero_tags]
        request = RequestCart.objects.create(owner=self.normal_user, status="active", reason="test shopping cart",
                                             staff_comment="this is an admin comment", staff=self.admin)
        another_request = RequestCart.objects.create(owner=self.admin, status="outstanding", reason="another req",
                                                     staff_comment="hi", staff=self.admin)
        requests_affected = [request, another_request]
        log_entry = LoggerUtility.log(self.admin, ActionEnum.ITEM_CREATED,  'Creating an item', self.normal_user,
                                      items_affected, requests_affected)
        equal_log(self, log_entry.id, self.admin, ActionEnum.ITEM_CREATED, 'Creating an item', self.normal_user,
                  items_affected, requests_affected)

    def test_utility_no_item_cart(self):
        log_entry = LoggerUtility.log(self.admin, ActionEnum.CUSTOM_FIELD_CREATED, 'Creating a custom field',
                                      self.normal_user)
        equal_log(self, log_entry.id, self.admin, ActionEnum.CUSTOM_FIELD_CREATED,  'Creating a custom field',
                  self.normal_user)

