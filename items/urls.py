from django.conf.urls import url
from items.views.item_view import ItemList, ItemDetail
from items.views.tag_view import TagCreation, TagDeletion

urlpatterns = [
    url(r'^$', ItemList.as_view()),
    url(r'^(?P<pk>[0-9]+)$', ItemDetail.as_view()),
    url(r'^tag/$', TagCreation.as_view()),
    url(r'^tag/(?P<pk>[0-9]+)$', TagDeletion.as_view()),
]
