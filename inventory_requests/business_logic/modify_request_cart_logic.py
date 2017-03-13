from inventoryProject.utility.queryset_functions import get_or_not_found
from items.models import Item


def can_approve_deny_cancel_request_cart(request_cart_to_modify, modification_type):
    for request in request_cart_to_modify.cart_disbursements.all():
        item = get_or_not_found(Item, pk=request.item.id)
        if item.quantity - request.quantity < 0 and modification_type == "approved":
            return False
    return request_cart_to_modify.status == "outstanding"


def approve_request_cart(request_cart_to_modify):
    for request in request_cart_to_modify.cart_disbursements.all():
        item = get_or_not_found(Item, pk=request.item.id)  # get item object based on item ID
        item.quantity = item.quantity - request.quantity
        item.save()
    # TODO add another for loop for the loans

