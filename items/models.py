from django.db import models

class Item(models.Model):
    name = models.CharField(max_length=100, unique=True)
    quantity = models.PositiveIntegerField(default=0)
    model_number = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=1000, blank=True, null=True)

class Tag(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='tags')
    tag = models.CharField(max_length=100)

