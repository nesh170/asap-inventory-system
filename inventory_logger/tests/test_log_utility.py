from django.contrib.auth.models import User
from django.test import TestCase

from inventory_logger.log_exceptions import InvalidLoggerError
from inventory_logger.models import Log
from inventory_logger.utility.logger import LoggerUtility

ADMIN_USERNAME = 'test'
ADMIN_PASSWORD = 'testPassword'

USER_USERNAME = 'user'
USER_PASSWORD = 'masalaPassword'


def equal_log(test_equal, log_id, user, action, description):
    log_entry = Log.objects.get(pk=log_id)
    test_equal.assertEqual(log_entry.user, user)
    test_equal.assertEqual(log_entry.action, action)
    test_equal.assertEqual(log_entry.log_text, description)


class LogUtilityTestCase(TestCase):
    def setUp(self):
        User.objects.create_superuser(ADMIN_USERNAME, 'test@test.com', ADMIN_PASSWORD)
        User.objects.create_user(USER_USERNAME, 'user@testforlife.com', USER_PASSWORD)

    def test_utility_admin_user(self):
        log_id = LoggerUtility.log(ADMIN_USERNAME, 'deploy', 'we are deploying a life lesson')
        equal_log(self, log_id, ADMIN_USERNAME, 'deploy', 'we are deploying a life lesson')

    def test_utility_as_system(self):
        log_id = LoggerUtility.log_as_system('destroy', 'deleted many items from the db')
        equal_log(self, log_id, 'system', 'destroy', 'deleted many items from the db')

    def test_invalid_logger_error_exception_non_admin(self):
        success_error = False
        try:
            LoggerUtility.log(USER_USERNAME, 'not possible', 'this will give an error')
        except InvalidLoggerError:
            success_error = True
        self.assertEqual(success_error, True)

    def test_invalid_logger_error_exception_not_in_user_db(self):
        success_error = False
        try:
            LoggerUtility.log('lololol45634', 'not possible', 'this will give an error')
        except InvalidLoggerError:
            success_error = True
        self.assertEqual(success_error, True)
