from django.conf.urls import url

#from inventory_logger.views.action_view import ActionList
from inventory_transaction_logger.views.log_view import LogList, ViewDetailedLog


urlpatterns = [
    url(r'^$', LogList.as_view(), name='log-list'),
    url(r'^detailed/(?P<pk>[0-9]+)/$', ViewDetailedLog.as_view(), name='detailed-log'),
    # url(r'^action/$', ActionList.as_view(), name='action-list')
]
