from django.contrib.auth.models import User
from django.db import models

from items.models import Item
from inventory_shopping_cart.models import ShoppingCart



class Action(models.Model):
    color = models.CharField(max_length=9, unique=True)
    tag = models.CharField(max_length=100, unique=True)

    def __str__(self):
        action_string = "{tag} : {color}".format
        return action_string(tag=self.tag, color=self.color)


class Log(models.Model):
    initiating_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='initiator')
    nature = models.ForeignKey(Action, on_delete=models.CASCADE, related_name='nature')
    timestamp = models.DateTimeField(auto_now=True)
    affected_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='affected', null=True, blank=True)

    def __str__(self):
        log_string = "{nature} was by {initiator} to {affected} on {timestamp}".format
        return log_string(nature=self.nature.tag, initiator=self.initiating_user.username,
                          affected=self.affected_user.username, timestamp=self.timestamp)

class ItemLog(models.Model):
    log = models.ForeignKey(Log, on_delete=models.CASCADE, related_name='item_log')
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='item')

    def __str__(self):
        item_log_string = "{log} : {item}".format
        return item_log_string(log=self.log.nature.tag, item=self.item.name)

class ShoppingCartLog(models.Model):
    log = models.ForeignKey(Log, on_delete=models.CASCADE, related_name='cart_log')
    cart = models.ForeignKey(ShoppingCart, on_delete=models.CASCADE, related_name='cart')


