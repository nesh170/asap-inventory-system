from inventory_transaction_logger.models import Log, Action, ItemLog, ShoppingCartLog


class LoggerUtility:
    @staticmethod
    def log(initiating_user, nature_enum, affected_user, comment, items_affected = None, carts_affected = None):
        action = Action.objects.get(tag=nature_enum.value)
        log_entry = Log.objects.create(initiating_user=initiating_user, nature=action, affected_user=affected_user, comment=comment)
        [ItemLog.objects.create(log=log_entry, item=item) for item in
         items_affected] if items_affected is not None else []
        [ShoppingCartLog.objects.create(log=log_entry, shopping_cart=cart) for cart in
         carts_affected] if carts_affected is not None else []

        for item in items_affected:
            ItemLog.objects.create(log=log_entry, item=item)
        for cart in carts_affected:
            ShoppingCartLog.objects.create(log=log_entry, shopping_cart=cart)
        return log_entry
