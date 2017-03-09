from django.db import models

class RequestTable(models.Model):
    item = models.ForeignKey('items.Item', null=True, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    shopping_cart = models.ForeignKey('inventory_shopping_cart.ShoppingCart', on_delete=models.CASCADE, related_name='requests')

    def __str__(self):
        request_string = "Request has the following parameters: item: {item}, quantity_requested: {quantity}," \
                         " shopping_cart_id: {shopping_cart_id}".format
        return request_string(item=self.item, quantity=self.quantity, shopping_cart_id=self.shopping_cart)