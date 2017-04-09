from datetime import datetime

from items.models.item_models import Item


def clear_asset(loan):
    for asset in loan.assets.all():
        asset.loan = None
        asset.save()


def return_loan_logic(loan, quantity=None):
    if loan.returned_timestamp is None and loan.loaned_timestamp is not None and loan.returned_quantity < loan.quantity:
        if quantity is None or loan.returned_quantity + quantity == loan.quantity:
            loan.returned_timestamp = datetime.now()
            quantity = loan.quantity
            new_returned_quantity = quantity
        else:
            new_returned_quantity = loan.returned_quantity + quantity
        if loan.returned_quantity + quantity > loan.quantity and quantity != loan.quantity:
            return False
        item = Item.objects.get(pk=loan.item.id)
        item.quantity = item.quantity + quantity
        item.save()
        loan.returned_quantity = new_returned_quantity
        loan.save()
        return True
    return False
