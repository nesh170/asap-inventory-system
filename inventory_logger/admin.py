from django.contrib import admin
from inventory_logger.models import Log, Action

# Register your models here.

admin.site.register(Log)
admin.site.register(Action)
