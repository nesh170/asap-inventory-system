from django.db import models

from items.models import Item


class RequestCart(models.Model):
    owner = models.ForeignKey('auth.User', related_name='request_owner', on_delete=models.CASCADE, null=True)
    status = models.CharField(max_length=16, choices=[
        ('outstanding', 'outstanding'), ('approved', 'approved'),
        ('cancelled', 'cancelled'), ('denied', 'denied'), ('active', 'active'), ('fulfilled', 'fulfilled')],
                              default='active')
    reason = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    staff = models.ForeignKey('auth.User', related_name='request_staff', on_delete=models.CASCADE, null=True,
                              limit_choices_to={'is_staff': True})
    staff_timestamp = models.DateTimeField(null=True, blank=True)
    staff_comment = models.TextField(null=True, blank=True)


class Disbursement(models.Model):
    cart = models.ForeignKey(RequestCart, related_name='cart_disbursements', on_delete=models.CASCADE)
    item = models.ForeignKey(Item, related_name='disbursement_items', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        disbursement_str = "{cart_id} : {cart_owner} was disbursed {item_name} : {quantity}".format
        return disbursement_str(cart_owner=self.cart.owner, cart_id=self.cart.id, item_name=self.item.name,
                                quantity=self.quantity)

    class Meta:
        unique_together = ('cart', 'item',)


class Loan(models.Model):
    cart = models.ForeignKey(RequestCart, related_name='cart_loans', on_delete=models.CASCADE)
    item = models.ForeignKey(Item, related_name='loan_items', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    loaned_timestamp = models.DateTimeField(null=True, blank=True)
    returned_timestamp = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        loan_str = "{cart_id} : {cart_owner} was loaned {item_name} : {quantity}".format
        return loan_str(cart_owner=self.cart.owner, cart_id=self.cart.id, item_name=self.item.name,
                        quantity=self.quantity)

    class Meta:
        unique_together = ('cart', 'item',)



