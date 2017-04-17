from inventory_email_support.models import SubscribedManagers
from inventory_email_support.utility.email_utility import EmailUtility


def send_email_with_item_under_threshold(item):
    email_list = SubscribedManagers.objects.all().values_list('member__email', flat=True)[::1]
    for email in email_list:
        EmailUtility.email(recipient=email, template='minimum_stock_reached',
                           context={'name': item.name, 'quantity': item.quantity,
                                    'minimum_stock': item.minimum_stock},
                           subject="{Item} reached minimum quantity".format(Item=item.name),
                           have_bcc=False)
