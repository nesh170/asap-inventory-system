from datetime import datetime

from items.models import Item


def return_loan_logic(loan, quantity=None):
    if loan.returned_timestamp is None and loan.loaned_timestamp is not None and loan.returned_quantity < loan.quantity:
        if quantity is None or loan.returned_quantity + quantity == loan.quantity:
            loan.returned_timestamp = datetime.now()
            quantity = loan.quantity
        if loan.returned_quantity + quantity > loan.quantity and quantity != loan.quantity:
            return False
        item = Item.objects.get(pk=loan.item.id)
        item.quantity = item.quantity + quantity
        item.save()
        loan.returned_quantity = quantity
        loan.save()
        return True
    return False
