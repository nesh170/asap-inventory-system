from django.conf.urls import url

from items.views.item_view import ItemList, ItemDetail
from items.views.tag_view import TagDeletion, TagList, UniqueTagList

urlpatterns = [
    url(r'^$', ItemList.as_view(), name='item-list'),
    url(r'^(?P<pk>[0-9]+)$', ItemDetail.as_view(), name='item-detail'),
    url(r'^tag/$', TagList.as_view(), name='tag-list'),
    url(r'^tag/(?P<pk>[0-9]+)$', TagDeletion.as_view(), name='tag-deletion'),
    url(r'^tag/unique/$', UniqueTagList.as_view(), name='unique-tag-list'),
]
