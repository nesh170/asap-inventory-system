from django.conf.urls import url

from inventory_requests.views.RequestCartList import RequestCartList
from inventory_requests.views.ActiveSendDetailedRequestCart import ViewDetailedRequestCart, ActiveRequestCart, SendCart
from inventory_shopping_cart_request.views.ShoppingCartRequestView import ShoppingCartRequestList, DeleteShoppingCartRequest, ModifyQuantityRequested
from inventory_shopping_cart.views.ModifyShoppingCart import ApproveShoppingCart, DenyShoppingCart, CancelShoppingCart
urlpatterns = [
    url(r'^$', RequestCartList.as_view(), name='request-cart-list'),
    url(r'^detailed/(?P<pk>[0-9]+)/$', ViewDetailedRequestCart.as_view(), name='detailed-request-cart'),
    url(r'^active/$', ActiveRequestCart.as_view(), name='active-cart'),
    url(r'^addItem/$', ShoppingCartRequestList.as_view(), name='add-to-cart'),
    # url(r'^deleteItem/(?P<pk>[0-9]+)/$', DeleteShoppingCartRequest.as_view(), name='delete-from-cart'),
    url(r'^send/(?P<pk>[0-9]+)/$', SendCart.as_view(), name='send-cart'),
    # url(r'^modifyQuantityRequested/(?P<pk>[0-9]+)/$', ModifyQuantityRequested.as_view(), name='modify-quantity-requested'),
    # url(r'^approve/(?P<pk>[0-9]+)/$', ApproveShoppingCart.as_view(), name='approve-shopping-cart'),
    # url(r'^cancel/(?P<pk>[0-9]+)/$', CancelShoppingCart.as_view(), name='cancel-shopping-cart'),
    # url(r'^deny/(?P<pk>[0-9]+)/$', DenyShoppingCart.as_view(), name='deny-shopping-cart'),

]
