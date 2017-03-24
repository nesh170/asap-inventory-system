from django.contrib import admin

from inventory_email_support.models import SubscribedManagers, SubjectTag, LoanReminderSchedule

admin.site.register(SubscribedManagers)
admin.site.register(SubjectTag)
admin.site.register(LoanReminderSchedule)
