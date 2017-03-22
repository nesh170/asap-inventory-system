from django.contrib import admin

from inventory_email.models import SubscribedManagers, SubjectTag

admin.site.register(SubscribedManagers)
admin.site.register(SubjectTag)