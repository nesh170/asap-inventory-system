from django.contrib import admin

from inventory_requests.models import RequestCart, Disbursement, Loan

admin.site.register(RequestCart)
admin.site.register(Disbursement)
admin.site.register(Loan)
