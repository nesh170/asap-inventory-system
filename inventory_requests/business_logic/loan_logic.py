from datetime import datetime

from inventory_requests.business_logic.modify_request_cart_logic import get_backfill_quantity
from items.models.item_models import Item


def clear_asset(loan):
    for asset in loan.assets.all():
        asset.loan = None
        asset.save()


def match_loan_asset(loan, asset):
    return (asset and loan.assets.filter(pk=asset.id).exists()) or not asset


def return_loan_logic(loan, quantity=None, asset=None):
    if loan.returned_timestamp is None and loan.loaned_timestamp is not None \
            and loan.returned_quantity < loan.quantity and match_loan_asset(loan, asset):
        max_quantity_to_return = (loan.quantity - get_backfill_quantity(loan.backfill_loan, backfill_transit=True))
        if quantity is None or (loan.returned_quantity + quantity) == max_quantity_to_return:
            # this case means return everything :/
            loan.returned_timestamp = datetime.now()
            quantity = max_quantity_to_return  # condition A
            new_returned_quantity = quantity
        else:
            # this is for partial return
            new_returned_quantity = loan.returned_quantity + quantity
        if loan.returned_quantity + quantity > max_quantity_to_return and quantity != max_quantity_to_return:
            # test whether the returned quantity + the quantity cannot be greater than the max_quantity to return
            # the first case will occur when condition A occurs, hence to prevent fail the second case needs to occur
            return False
        item = Item.objects.get(pk=loan.item.id)
        item.quantity = item.quantity + quantity
        item.save()
        loan.returned_quantity = new_returned_quantity
        loan.save()
        return True
    return False
