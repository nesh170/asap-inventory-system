from django.contrib import admin

from inventory_transaction_logger.models import Log, Action, ItemLog, RequestCartLog

admin.site.register(Log)
admin.site.register(Action)
admin.site.register(ItemLog)
admin.site.register(RequestCartLog)

