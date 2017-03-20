from datetime import datetime

from inventoryProject.utility.queryset_functions import get_or_not_found
from items.models import Item


def precheck_item(request, modification_type):
    item = get_or_not_found(Item, pk=request.item.id)
    return not (item.quantity - request.quantity < 0 and
                (modification_type == "approved" or modification_type == "disburse"))


def can_modify_cart_status(request):
    return request.status == "outstanding" or (request.staff is not None and request.status == "active")


def can_approve_disburse_request_cart(request_cart_to_modify, modification_type):
    disbursements = [precheck_item(request, modification_type) for
                     request in request_cart_to_modify.cart_disbursements.all()]
    loans = [precheck_item(request, modification_type) for request in request_cart_to_modify.cart_loans.all()]
    return not(False in disbursements or False in loans) and can_modify_cart_status(request_cart_to_modify)


def subtract_item(request):
    item = get_or_not_found(Item, pk=request.item.id)  # get item object based on item ID
    item.quantity = item.quantity - request.quantity
    item.save()


def subtract_item_in_cart(request_cart_to_modify):
    [subtract_item(request) for request in request_cart_to_modify.cart_disbursements.all()]
    [subtract_item(request) for request in request_cart_to_modify.cart_loans.all()]


def start_loan(request):
    for loan in request.cart_loans.all():
        loan.loaned_timestamp = datetime.now()
        loan.save()


def can_convert_request_type(cart, user):
    return cart.status in ('fulfilled', 'outstanding', 'approved') and user.is_staff
