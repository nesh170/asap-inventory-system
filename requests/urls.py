from django.conf.urls import url
from requests import views

urlpatterns = [
    url(r'^requests/$', views.RequestList.as_view()),
    url(r'^requests/(?P<pk>[0-9]+)/$', views.ViewDetailedRequest.as_view()),
    url(r'^userRequests', views.RequestListUser.as_view()),
    url(r'^createRequest', views.CreateRequest.as_view()),
    url(r'^modifyRequest/(?P<pk>[0-9]+)/$', views.ModifyRequest.as_view()),
]
