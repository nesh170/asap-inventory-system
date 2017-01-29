from django.conf.urls import url
from inventory_requests.views.RequestList import RequestList
from inventory_requests.views.DetailedRequest import ViewDetailedRequest
from inventory_requests.views.RequestListUser import RequestListUser
from inventory_requests.views.CreateRequest import CreateRequest
from inventory_requests.views.ModifyRequest import ModifyRequest
urlpatterns = [
    url(r'^requests/$', RequestList.as_view(), name='requests-list'),
    url(r'^requests/(?P<pk>[0-9]+)/$', ViewDetailedRequest.as_view(), name='detailed-request'),
    url(r'^userRequests', RequestListUser.as_view(), name='user-requests'),
    url(r'^createRequest', CreateRequest.as_view(), name='create-request'),
    url(r'^modifyRequest/(?P<pk>[0-9]+)/$', ModifyRequest.as_view(), name='modify-request'),
]
