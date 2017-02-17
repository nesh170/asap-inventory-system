from django.conf.urls import url

from inventory_shopping_cart_request.views.ShoppingCartRequestView import ShoppingCartRequestList
urlpatterns = [
    url(r'^$', ShoppingCartRequestList.as_view(), name='shopping-cart-requests-list'),

]