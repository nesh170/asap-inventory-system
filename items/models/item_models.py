from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from items.logic.email_logic import send_email_with_item_under_threshold

ITEM_HEADERS = ['name', 'quantity', 'description', 'model_number', 'tags', 'minimum_stock', 'track_minimum_stock']


class Item(models.Model):
    name = models.CharField(max_length=100, unique=True)
    quantity = models.PositiveIntegerField(default=0)
    model_number = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    minimum_stock = models.PositiveIntegerField(default=0)
    track_minimum_stock = models.BooleanField(default=False)

    def __str__(self):
        item_string = "{name} : {quantity}".format
        return item_string(name=self.name, quantity=self.quantity)


@receiver(post_save, sender=Item)
def minimum_quantity_callback(instance, **kwargs):
    if instance.quantity < instance.minimum_stock and instance.track_minimum_stock:
        send_email_with_item_under_threshold(instance)


class Tag(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='tags')
    tag = models.CharField(max_length=100)

    def __str__(self):
        tag_string = "Tag {tag} with item {item}".format
        return tag_string(tag=self.tag, item=self.item.name)
