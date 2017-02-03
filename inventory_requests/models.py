from django.db import models


class Request(models.Model):
    owner = models.ForeignKey('auth.User', related_name='owner', on_delete=models.CASCADE, null=True)
    status = models.CharField(max_length=16, choices=[
        ('outstanding', 'outstanding'), ('approved', 'approved'),
        ('cancelled', 'cancelled'), ('denied', 'denied')], default='outstanding')
    item = models.ForeignKey('items.Item', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)
    reason = models.TextField()
    timestamp = models.DateTimeField(auto_now=True)
    admin_timestamp = models.DateTimeField(null=True)
    admin_comment = models.TextField(null=True, blank=True)
    admin = models.ForeignKey('auth.User', related_name='admin', on_delete=models.CASCADE, null=True)

    def __str__(self):
        request_string = "Request has the following parameters: owner: {owner}, status: {status}, item: {item}, quantity: {quantity}, reason: {reason}, timestamp: {timestamp}, admin_comment: {admin_comment}, admin: {admin}".format
        return request_string(owner=self.owner, status=self.status, item=self.item, quantity=self.quantity, reason=self.reason, timestamp=self.timestamp, admin_timestamp=self.admin_timestamp, admin_comment=self.admin_comment, admin=self.admin)




