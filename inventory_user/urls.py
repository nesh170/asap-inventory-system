from django.conf.urls import url

from inventory_user.views.user_view import InventoryUserList
from items.views.item_view import ItemList, ItemDetail
from items.views.tag_view import TagDeletion, TagList

urlpatterns = [
    url(r'^$', InventoryUserList.as_view(), name='user-list'),
]
