from django.contrib.auth.models import User
from django.db import models

from items.models import Item


class Cart(models.Model):
    disburser = models.ForeignKey(User, on_delete=models.CASCADE, related_name='disburser', limit_choices_to={'is_staff': True})
    comment = models.TextField(null=True, blank=True)
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='receiver', null=True, blank=True)
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        disbursement_cart_string = "Cart by {admin} for {receiver} has {items_quantity} items".format
        return disbursement_cart_string(admin=self.disburser if self.disburser is not None else 'NULL',
                                        receiver=self.receiver if self.disburser is not None else 'NULL',
                                        items_quantity=self.disbursements.count())


class Disbursement(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='disbursements')
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='disbursed')
    quantity = models.PositiveIntegerField()

    def __str__(self):
        disbursement_string = "{admin} gave {quantity} {item} to {receiver} on {timestamp}".format
        return disbursement_string(quantity=self.quantity, item=self.item, admin=self.cart.disburser,
                                   receiver=self.cart.receiver, timestamp=self.cart.timestamp)
