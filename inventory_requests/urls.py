from django.conf.urls import url

from inventory_requests.views.RequestCartList import RequestCartList
from inventory_requests.views.ActiveSendDetailedRequestCart import ViewDetailedRequestCart, ActiveRequestCart, SendCart
from inventory_requests.views.CreateDeleteModifyDisbursement import CreateDisbursement, DeleteDisbursement, ModifyQuantityRequested
from inventory_requests.views.ModifyRequestCart import ApproveRequestCart, DenyRequestCart, CancelRequestCart, \
    FulfilRequestCart, DispenseRequestCart

urlpatterns = [
    url(r'^$', RequestCartList.as_view(), name='request-cart-list'),
    url(r'^(?P<pk>[0-9]+)$', ViewDetailedRequestCart.as_view(), name='detailed-request-cart'),
    url(r'^active/$', ActiveRequestCart.as_view(), name='active-cart'),
    url(r'^addItem/$', CreateDisbursement.as_view(), name='add-to-cart'),
    url(r'^deleteItem/(?P<pk>[0-9]+)/$', DeleteDisbursement.as_view(), name='delete-from-cart'),
    url(r'^send/(?P<pk>[0-9]+)/$', SendCart.as_view(), name='send-cart'),
    url(r'^modifyQuantityRequested/(?P<pk>[0-9]+)/$', ModifyQuantityRequested.as_view(),
        name='modify-quantity-requested'),
    url(r'^approve/(?P<pk>[0-9]+)/$', ApproveRequestCart.as_view(), name='approve-request-cart'),
    url(r'^cancel/(?P<pk>[0-9]+)/$', CancelRequestCart.as_view(), name='cancel-request-cart'),
    url(r'^deny/(?P<pk>[0-9]+)/$', DenyRequestCart.as_view(), name='deny-request-cart'),
    url(r'^dispense/(?P<pk>[0-9]+)/$', DispenseRequestCart.as_view(), name='dispense-request-cart'),
    url(r'^fulfil/(?P<pk>[0-9]+)/$', FulfilRequestCart.as_view(), name='fulfil-request-cart'),
]
