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





