from django.contrib.auth.models import User
from django.db import models

from items.models import Item


class Disbursement(models.Model):
    disburser = models.ForeignKey(User, on_delete=models.CASCADE, related_name='disburser')
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='disbursed')
    quantity = models.PositiveIntegerField()
    timestamp = models.DateTimeField(auto_now=True)
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='receiver')

    def __str__(self):
        disbursement_string = "{admin} gave {quantity} {item} to {receiver} on {timestamp}".format
        return disbursement_string(admin=self.disburser, quantity=self.quantity, item=self.item.name, receiver=self.receiver, timestamp=self.timestamp)
