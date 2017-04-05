from django.conf.urls import url

from inventory_requests.views.CreateDeleteModifyLoan import CreateLoan, DeleteLoan, ReturnLoan, ReturnAllLoans
from inventory_requests.views.RequestCartList import RequestCartList
from inventory_requests.views.ActiveSendDetailedRequestCart import ViewDetailedRequestCart, ActiveRequestCart, SendCart
from inventory_requests.views.CreateDeleteModifyDisbursement import CreateDisbursement, DeleteDisbursement
from inventory_requests.views.ModifyRequestCart import ApproveRequestCart, DenyRequestCart, CancelRequestCart, \
    FulfillRequestCart, DispenseRequestCart, ModifyQuantityRequested, ConvertRequestType
from inventory_requests.views.BackfillView import ConvertLoanToBackfill

urlpatterns = [
    url(r'^$', RequestCartList.as_view(), name='request-cart-list'),
    url(r'^(?P<pk>[0-9]+)$', ViewDetailedRequestCart.as_view(), name='detailed-request-cart'),
    url(r'^active/$', ActiveRequestCart.as_view(), name='active-cart'),
    url(r'^disbursement/$', CreateDisbursement.as_view(), name='add-to-cart'),
    url(r'^disbursement/deleteItem/(?P<pk>[0-9]+)/$', DeleteDisbursement.as_view(), name='delete-from-cart'),
    url(r'^send/(?P<pk>[0-9]+)/$', SendCart.as_view(), name='send-cart'),
    url(r'^modifyQuantityRequested/(?P<pk>[0-9]+)/$', ModifyQuantityRequested.as_view(),
        name='modify-quantity-requested'),
    url(r'^approve/(?P<pk>[0-9]+)/$', ApproveRequestCart.as_view(), name='approve-request-cart'),
    url(r'^cancel/(?P<pk>[0-9]+)/$', CancelRequestCart.as_view(), name='cancel-request-cart'),
    url(r'^deny/(?P<pk>[0-9]+)/$', DenyRequestCart.as_view(), name='deny-request-cart'),
    url(r'^dispense/(?P<pk>[0-9]+)/$', DispenseRequestCart.as_view(), name='dispense-request-cart'),
    url(r'^fulfill/(?P<pk>[0-9]+)/$', FulfillRequestCart.as_view(), name='fulfill-request-cart'),
    url(r'^loan/$', CreateLoan.as_view(), name='add-loan-to-cart'),
    url(r'^loan/deleteItem/(?P<pk>[0-9]+)/$', DeleteLoan.as_view(), name='delete-loan-from-cart'),
    url(r'^loan/returnItem/(?P<pk>[0-9]+)/$', ReturnLoan.as_view(), name='return-loan-from-cart'),
    url(r'^returnAllLoans/(?P<pk>[0-9]+)/$', ReturnAllLoans.as_view(), name='return-all-loans-from-cart'),
    url(r'^convertRequestType/$', ConvertRequestType.as_view(), name='convert-request-type'),
    url(r'^backfill/convertLoan/$', ConvertLoanToBackfill.as_view(), name='convert-loan-to-backfill')

]
