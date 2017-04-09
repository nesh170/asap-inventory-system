from django.db import models

ITEM_HEADERS = ['name', 'quantity', 'description', 'model_number', 'tags', 'minimum_stock', 'track_minimum_stock']


class Item(models.Model):
    name = models.CharField(max_length=100, unique=True)
    quantity = models.PositiveIntegerField(default=0)
    model_number = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    minimum_stock = models.PositiveIntegerField(default=0)
    track_minimum_stock = models.BooleanField(default=False)
    is_asset = models.BooleanField(default=False)

    def __str__(self):
        item_string = "{name} : {quantity}".format
        return item_string(name=self.name, quantity=self.quantity)


class Tag(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='tags')
    tag = models.CharField(max_length=100)

    def __str__(self):
        tag_string = "Tag {tag} with item {item}".format
        return tag_string(tag=self.tag, item=self.item.name)
