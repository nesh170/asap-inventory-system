from datetime import datetime

from items.models import Item


def return_loan_logic(loan, quantity=None):
    if loan.returned_timestamp is None and loan.loaned_timestamp is not None:
        if quantity is None or quantity == loan.quantity:
            loan.returned_timestamp = datetime.now()
            loan.save()
            quantity = loan.quantity
        item = Item.objects.get(pk=loan.item.id)
        item.quantity = item.quantity + quantity
        item.save()
        return True
    return False
