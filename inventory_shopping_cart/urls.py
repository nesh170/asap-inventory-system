from django.conf.urls import url

from inventory_shopping_cart.views.ShoppingCartView import ShoppingCartList
from inventory_shopping_cart.views.DetailedShoppingCart import ViewDetailedShoppingCart, ActiveShoppingCart
from inventory_shopping_cart_request.views.ShoppingCartRequestView import ShoppingCartRequestList, DeleteShoppingCartRequest
urlpatterns = [
    url(r'^$', ShoppingCartList.as_view(), name='shopping-cart-list'),
    url(r'^detailed/(?P<pk>[0-9]+)/$', ViewDetailedShoppingCart.as_view(), name='detailed-shopping-cart'),
    url(r'^active/$', ActiveShoppingCart.as_view(), name='active-cart'),
    url(r'^addItem/$', ShoppingCartRequestList.as_view(), name='add-to-cart'),
    url(r'^deleteItem/(?P<pk>[0-9]+)/$', DeleteShoppingCartRequest.as_view(), name='delete-from-cart'),

]
