from django.db import models

class RequestTable(models.Model):
    item = models.ForeignKey('items.Item', null=True, on_delete=models.SET_NULL)
    quantity_requested = models.PositiveIntegerField(default=0)
    #TODO: THE ON_DELETE HAS TO BE FIXED
    shopping_cart = models.ForeignKey('inventory_shopping_cart.ShoppingCart', on_delete=models.CASCADE)

    def __str__(self):
        request_string = "Request has the following parameters: item: {item}, quantity: {quantity}, shopping_cart_id: {shopping_cart_id}".format
        return request_string(item=self.item, quantity=self.quantity, shopping_cart_id=self.shopping_cart)