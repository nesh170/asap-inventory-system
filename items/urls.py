from django.conf.urls import url

from items.views.csv_view import export_item_view, ItemCsvImport
from items.views.field_view import FieldList, IntFieldUpdate, FloatFieldUpdate, ShortTextFieldUpdate, \
    LongTextFieldUpdate, FieldDetailed
from items.views.item_view import ItemList, ItemDetail, UniqueItemList, ItemQuantityModification
from items.views.tag_view import TagDeletion, TagList, UniqueTagList

urlpatterns = [
    url(r'^$', ItemList.as_view(), name='item-list'),
    url(r'^unique/$', UniqueItemList.as_view(), name='unique-item-list'),
    url(r'^(?P<pk>[0-9]+)$', ItemDetail.as_view(), name='item-detail'),
    url(r'^tag/$', TagList.as_view(), name='tag-list'),
    url(r'^tag/(?P<pk>[0-9]+)$', TagDeletion.as_view(), name='tag-deletion'),
    url(r'^tag/unique/$', UniqueTagList.as_view(), name='unique-tag-list'),
    url(r'^field/$', FieldList.as_view(), name='field-list'),
    url(r'^field/(?P<pk>[0-9]+)$', FieldDetailed.as_view(), name='field-detail'),
    url(r'^field/int/(?P<pk>[0-9]+)$', IntFieldUpdate.as_view(), name='int-field-update'),
    url(r'^field/float/(?P<pk>[0-9]+)$', FloatFieldUpdate.as_view(), name='float-field-update'),
    url(r'^field/short_text/(?P<pk>[0-9]+)$', ShortTextFieldUpdate.as_view(), name='short-text-field-update'),
    url(r'^field/long_text/(?P<pk>[0-9]+)$', LongTextFieldUpdate.as_view(), name='long-text-field-update'),
    url(r'^quantity$', ItemQuantityModification.as_view(), name='item-quantity-modification'),
    url(r'^csv/export$', export_item_view, name='export-item'),
    url(r'^csv/import$', ItemCsvImport.as_view(), name='import-item')
]
