from datetime import datetime

from items.models import Item


def return_loan_logic(loan):
    if loan.returned_timestamp is None and loan.loaned_timestamp is not None:
        loan.returned_timestamp = datetime.now()
        loan.save()
        item = Item.objects.get(pk=loan.item.id)
        item.quantity = item.quantity + loan.quantity
        item.save()
        return True
    return False
