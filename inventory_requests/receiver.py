from django.db.models.signals import post_delete
from django.dispatch import receiver

from items.models import Item


@receiver(post_delete, sender=Item)
def request_callback(sender, **kwargs):
    print("Item deleted")