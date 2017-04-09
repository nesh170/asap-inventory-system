from django.db.models.signals import post_save
from django.dispatch import receiver

from items.logic.asset_logic import create_assets
from items.logic.email_logic import send_email_with_item_under_threshold
from items.models.item_models import Item


@receiver(post_save, sender=Item)
def changed_to_asset(instance, **kwargs):
    if instance.is_asset:
        create_assets(item=instance)


@receiver(post_save, sender=Item)
def minimum_quantity_callback(instance, **kwargs):
    if instance.quantity < instance.minimum_stock and instance.track_minimum_stock:
        send_email_with_item_under_threshold(instance)