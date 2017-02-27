from django.db import models


class ShoppingCart(models.Model):
    owner = models.ForeignKey('auth.User', related_name='shopping_cart_owner', on_delete=models.CASCADE, null=True)
    status = models.CharField(max_length=16, choices=[
        ('outstanding', 'outstanding'), ('approved', 'approved'),
        ('cancelled', 'cancelled'), ('denied', 'denied'), ('active', 'active')], default='active')
    reason = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now=True)
    admin_timestamp = models.DateTimeField(null=True)
    admin_comment = models.TextField(null=True, blank=True)
    admin = models.ForeignKey('auth.User', related_name='shopping_cart_admin', on_delete=models.CASCADE, null=True, limit_choices_to={'is_staff': True})

    def __str__(self):
        shopping_cart_string = "Request has the following parameters: owner: {owner}, status: {status}, reason: {reason}, timestamp: {timestamp}, admin_comment: {admin_comment}, admin: {admin}".format
        return shopping_cart_string(owner=self.owner, status=self.status, reason=self.reason, timestamp=self.timestamp, admin_timestamp=self.admin_timestamp, admin_comment=self.admin_comment, admin=self.admin)