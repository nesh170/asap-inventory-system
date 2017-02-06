import datetime
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver

from inventory_logger.action_enum import ActionEnum
from inventory_logger.utility.logger import LoggerUtility
from items.models import Item


class Request(models.Model):
    owner = models.ForeignKey('auth.User', related_name='owner', on_delete=models.CASCADE, null=True)
    status = models.CharField(max_length=16, choices=[
        ('outstanding', 'outstanding'), ('approved', 'approved'),
        ('cancelled', 'cancelled'), ('denied', 'denied')], default='outstanding')
    item = models.ForeignKey('items.Item', null=True, on_delete=models.SET_NULL)
    quantity = models.PositiveIntegerField(default=0)
    reason = models.TextField()
    timestamp = models.DateTimeField(auto_now=True)
    admin_timestamp = models.DateTimeField(null=True)
    admin_comment = models.TextField(null=True, blank=True)
    admin = models.ForeignKey('auth.User', related_name='admin', on_delete=models.CASCADE, null=True)

    def __str__(self):
        request_string = "Request has the following parameters: owner: {owner}, status: {status}, item: {item}, quantity: {quantity}, reason: {reason}, timestamp: {timestamp}, admin_comment: {admin_comment}, admin: {admin}".format
        return request_string(owner=self.owner, status=self.status, item=self.item, quantity=self.quantity, reason=self.reason, timestamp=self.timestamp, admin_timestamp=self.admin_timestamp, admin_comment=self.admin_comment, admin=self.admin)

    @receiver(pre_delete, sender=Item, dispatch_uid='item_got_deleted')
    def item_got_deleted(sender, instance, using, **kwargs):
        requests = Request.objects.filter(item=instance)
        for request in requests:
            request.admin_comment = instance.name + "has been deleted by admin"
            request.admin_timestamp = datetime.datetime.now()
            if request.status == 'outstanding':
                request.status = 'denied'
                LoggerUtility.log_as_system(ActionEnum.REQUEST_DENIED, 'Request:' + str(request.id) +
                                            ' denied due to item ' + str(instance.name) + " deletion")
            request.save()





