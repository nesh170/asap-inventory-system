from django.conf.urls import url

from inventory_requests.views.DetailedRequest import ViewDetailedRequest
from inventory_requests.views.ModifyRequest import ApproveRequest, CancelRequest, DenyRequest
from inventory_requests.views.RequestList import RequestList

urlpatterns = [
    url(r'^detailed/(?P<pk>[0-9]+)/$', ViewDetailedRequest.as_view(), name='detailed-request'),
    url(r'^approve/(?P<pk>[0-9]+)/$', ApproveRequest.as_view(), name='approve-request'),
    url(r'^cancel/(?P<pk>[0-9]+)/$', CancelRequest.as_view(), name='cancel-request'),
    url(r'^deny/(?P<pk>[0-9]+)/$', DenyRequest.as_view(), name='deny-request'),
    url(r'^$', RequestList.as_view(), name='requests-list'),

]
