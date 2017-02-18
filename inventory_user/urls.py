from django.conf.urls import url

from inventory_user.views.user_view import InventoryUserList, InventoryCurrentUser, InventoryUser, LargeUserList, \
    get_duke_access_token

urlpatterns = [
    url(r'^$', InventoryUserList.as_view(), name='user-list'),
    url(r'^large/$', LargeUserList.as_view(), name='large-user-list'),
    url(r'^current/$', InventoryCurrentUser.as_view(), name='user-current'),
    url(r'^(?P<pk>[0-9]+)$', InventoryUser.as_view(), name='user-detail'),
    url(r'^auth/duke$', get_duke_access_token, name='auth-duke')
]
