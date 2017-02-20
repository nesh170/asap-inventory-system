from django.conf.urls import url

from inventory_disbursements.views.disbursement_view import CartList, DisbursementCreation, DisbursementDeletion, \
    ActiveCart, CartSubmission

urlpatterns = [
    url(r'^$', CartList.as_view(), name='cart-list'),
    url(r'^(?P<pk>[0-9]+)$', CartSubmission.as_view(), name='cart-submission'),
    url(r'^active/$', ActiveCart.as_view(), name='active-cart'),
    url(r'^disbursements/(?P<pk>[0-9]+)$', DisbursementDeletion.as_view(), name='disbursement-deletion'),
    url(r'disbursements/create/', DisbursementCreation.as_view(), name='disbursement-creation')
]
