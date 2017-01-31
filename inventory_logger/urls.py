from django.conf.urls import url
from inventory_logger.views.log_view import LogList


urlpatterns = [
    url(r'^$', LogList.as_view(), name='log-list'),
]
