from django.contrib.auth.models import User
from inventory_logger.log_exceptions import InvalidLoggerError
from inventory_transaction_logger.models import Log, Action, ItemLog


class LoggerUtility:
    # @staticmethod
    # def log(initiating_user, nature, affected_user, items_affected):
    #     if (User.objects.filter(userninitiating_user)
    #     if user == 'system' or User.objects.filter(username=user, is_staff=True).exists():
    #         action = Action.objects.get(tag=action_enum.value)
    #         log_entry = Log.objects.create(user=user, action=action, description=description)
    #         return log_entry.id
    #     else:
    #         raise InvalidLoggerError(user, 'This user is not found in the database or is not the system')

    @staticmethod
    def log_as_system(action, description):
        return LoggerUtility.log('system', action, description)

