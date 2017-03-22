from inventory_transaction_logger.models import Log, Action, ItemLog, RequestCartLog


class LoggerUtility:
    @staticmethod
    def log(initiating_user, nature_enum, comment="", affected_user=None, items_affected=None,
            carts_affected=None):
        action = Action.objects.get(tag=nature_enum.value)
        if affected_user is not None:
            log_entry = Log.objects.create(initiating_user=initiating_user, nature=action,
                                           affected_user=affected_user, comment=comment)
        else:
            log_entry = Log.objects.create(initiating_user=initiating_user, nature=action, comment=comment)
        [ItemLog.objects.create(log=log_entry, item=item) for item in
         items_affected] if items_affected is not None else []
        [RequestCartLog.objects.create(log=log_entry, request_cart=cart) for cart in
         carts_affected] if carts_affected is not None else []
        return log_entry
