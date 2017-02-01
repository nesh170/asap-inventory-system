from django.conf.urls import url
from inventory_requests.views.RequestList import RequestList
from inventory_requests.views.DetailedRequest import ViewDetailedRequest
from inventory_requests.views.RequestListUser import RequestListUser
from inventory_requests.views.CreateRequest import CreateRequest
from inventory_requests.views.ModifyRequest import ApproveRequest, CancelRequest, DenyRequest
urlpatterns = [
    url(r'^requests/$', RequestList.as_view(), name='requests-list'),
    url(r'^requests/(?P<pk>[0-9]+)/$', ViewDetailedRequest.as_view(), name='detailed-request'),
    url(r'^userRequests', RequestListUser.as_view(), name='user-requests'),
    url(r'^createRequest', CreateRequest.as_view(), name='create-request'),
    url(r'^approveRequest/(?P<pk>[0-9]+)/$', ApproveRequest.as_view(), name='approve-request'),
    url(r'^cancelRequest/(?P<pk>[0-9]+)/$', CancelRequest.as_view(), name='cancel-request'),#add url for deny
    url(r'^denyRequest/(?P<pk>[0-9]+)/$', DenyRequest.as_view(), name='cancel-request'),  # add url for deny
]
