from django.conf.urls import url

from inventory_shopping_cart.views.ShoppingCartList import ShoppingCartList
from inventory_shopping_cart.views.DetailedShoppingCart import ViewDetailedShoppingCart, ActiveShoppingCart, SendCart
from inventory_shopping_cart_request.views.ShoppingCartRequestView import ShoppingCartRequestList, DeleteShoppingCartRequest, ModifyQuantity
from inventory_shopping_cart.views.ModifyShoppingCart import ApproveShoppingCart, DenyShoppingCart, CancelShoppingCart
urlpatterns = [
    url(r'^$', ShoppingCartList.as_view(), name='shopping-cart-list'),
    url(r'^detailed/(?P<pk>[0-9]+)/$', ViewDetailedShoppingCart.as_view(), name='detailed-shopping-cart'),
    url(r'^active/$', ActiveShoppingCart.as_view(), name='active-cart'),
    url(r'^addItem/$', ShoppingCartRequestList.as_view(), name='add-to-cart'),
    url(r'^deleteItem/(?P<pk>[0-9]+)/$', DeleteShoppingCartRequest.as_view(), name='delete-from-cart'),
    url(r'^send/(?P<pk>[0-9]+)/$', SendCart.as_view(), name='send-cart'),
    url(r'^modifyQuantity/(?P<pk>[0-9]+)/$', ModifyQuantity.as_view(), name='modify-quantity'),
    url(r'^approve/(?P<pk>[0-9]+)/$', ApproveShoppingCart.as_view(), name='approve-shopping-cart'),
    url(r'^cancel/(?P<pk>[0-9]+)/$', CancelShoppingCart.as_view(), name='cancel-shopping-cart'),
    url(r'^deny/(?P<pk>[0-9]+)/$', DenyShoppingCart.as_view(), name='deny-shopping-cart'),

]
