from django.contrib import admin

from inventory_disbursements.models import Disbursement, Cart

admin.site.register(Cart)
admin.site.register(Disbursement)


