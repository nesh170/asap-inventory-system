from django.contrib.auth.models import User
from django.test import TestCase

from inventory_logger.action_enum import ActionEnum
from inventory_logger.log_exceptions import InvalidLoggerError
from inventory_logger.models import Log, Action
from inventory_logger.utility.logger import LoggerUtility

ADMIN_USERNAME = 'test'
ADMIN_PASSWORD = 'testPassword'

USER_USERNAME = 'user'
USER_PASSWORD = 'masalaPassword'


def equal_log(test_equal, log_id, user, action, description):
    log_entry = Log.objects.get(pk=log_id)
    test_equal.assertEqual(log_entry.user, user)
    test_equal.assertEqual(log_entry.action.tag, action.value)
    test_equal.assertEqual(log_entry.description, description)


class LogUtilityTestCase(TestCase):
    def setUp(self):
        User.objects.create_superuser(ADMIN_USERNAME, 'test@test.com', ADMIN_PASSWORD)
        User.objects.create_user(USER_USERNAME, 'user@testforlife.com', USER_PASSWORD)
        Action.objects.create(color='1', tag='ITEM CREATED')
        Action.objects.create(color='2', tag='ITEM DESTROYED')
        Action.objects.create(color='3', tag='DISBURSED')
        Action.objects.create(color='4', tag='REQUEST CANCELLED')

    def test_utility_admin_user(self):
        log_id = LoggerUtility.log(ADMIN_USERNAME, ActionEnum.ITEM_CREATED, 'we are deploying a life lesson')
        equal_log(self, log_id, ADMIN_USERNAME, ActionEnum.ITEM_CREATED, 'we are deploying a life lesson')

    def test_utility_as_system(self):
        log_id = LoggerUtility.log_as_system(ActionEnum.ITEM_DESTROYED, 'deleted many items from the db')
        equal_log(self, log_id, 'system', ActionEnum.ITEM_DESTROYED, 'deleted many items from the db')

    def test_invalid_logger_error_exception_non_admin(self):
        success_error = False
        try:
            LoggerUtility.log(USER_USERNAME, ActionEnum.DISBURSED, 'this will give an error')
        except InvalidLoggerError:
            success_error = True
        self.assertEqual(success_error, True)

    def test_invalid_logger_error_exception_not_in_user_db(self):
        success_error = False
        try:
            LoggerUtility.log('lololol45634', ActionEnum.REQUEST_CANCELLED, 'this will give an error')
        except InvalidLoggerError:
            success_error = True
        self.assertEqual(success_error, True)
