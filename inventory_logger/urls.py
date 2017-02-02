from django.conf.urls import url

from inventory_logger.views.action_view import ActionList
from inventory_logger.views.log_view import LogList


urlpatterns = [
    url(r'^$', LogList.as_view(), name='log-list'),
    url(r'^action/$', ActionList.as_view(), name='action-list')
]
