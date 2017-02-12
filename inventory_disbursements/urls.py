from django.conf.urls import url

from inventory_disbursements.views.disbursement_view import DisbursementList

urlpatterns = [
    url(r'^$', DisbursementList.as_view(), name='disbursement-list'),
]
