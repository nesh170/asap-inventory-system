from django.contrib.auth.models import User
from inventory_logger.log_exceptions import InvalidLoggerError
from inventory_logger.models import Log


class LoggerUtility:
    @staticmethod
    def log(user, action, description):
        if user == 'system' or User.objects.filter(username=user, is_staff=True).exists():
            log_entry = Log.objects.create(user=user, action=action, log_text=description)
            return log_entry.id
        else:
            raise InvalidLoggerError(user, 'This user is not found in the database or is not the system')

    @staticmethod
    def log_as_system(action, description):
        return LoggerUtility.log('system', action, description)

