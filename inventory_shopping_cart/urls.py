from django.conf.urls import url

from inventory_shopping_cart.views.ShoppingCartView import ShoppingCartList
from inventory_shopping_cart.views.DetailedShoppingCart import ViewDetailedShoppingCart, ActiveShoppingCart

urlpatterns = [
    url(r'^$', ShoppingCartList.as_view(), name='shopping-cart-list'),
    url(r'^detailed/(?P<pk>[0-9]+)/$', ViewDetailedShoppingCart.as_view(), name='detailed-shopping-cart'),
    url(r'^active/$', ActiveShoppingCart.as_view(), name='active-cart'),

]
