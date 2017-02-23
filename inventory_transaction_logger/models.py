from django.contrib.auth.models import User
from django.db import models

from items.models import Item


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
    effected_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='affected')

    def __str__(self):
        log_string = "{nature} was by {initiator} to {affected} on {timestamp}".format
        return log_string(nature=self.nature.tag, initiator=self.initiating_user.username,
                          affected=self.effected_user.username, timestamp=self.timestamp)

class ItemLog(models.Model):
    log = models.ForeignKey(Log, on_delete=models.CASCADE, related_name='log')
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='item')

    def __str__(self):
        item_log_string = "{log} : {item}".format
        return item_log_string(log=self.log.nature.tag, item=self.item.name)


