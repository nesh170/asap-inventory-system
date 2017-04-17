from datetime import datetime
from functools import reduce

from rest_framework.exceptions import ParseError, MethodNotAllowed

from inventoryProject.utility.queryset_functions import get_or_not_found
from inventory_requests.models import RequestCart, Loan
from items.models.asset_models import Asset
from items.models.item_models import Item


def precheck_item(request):
    item = get_or_not_found(Item, pk=request.item.id)
    return not item.quantity - request.quantity < 0


def precheck_backfill(loan):
    total_quantity_requested = 0
    backfills_requested = loan.backfill_loan.filter(status='backfill_request').all()
    for backfill in backfills_requested:
        total_quantity_requested = total_quantity_requested + backfill.quantity
    return not loan.quantity - total_quantity_requested < 0


def can_modify_cart_status(request):
    return (request.status == "outstanding" and request.staff is None) or (request.staff is not None
                                                                           and request.status == "active")


def can_approve_disburse_request_cart(request_cart_to_modify):
    disbursements = [precheck_item(request) for
                     request in request_cart_to_modify.cart_disbursements.all()]
    loans = [precheck_item(request) for request in request_cart_to_modify.cart_loans.all()]
    backfills = [precheck_backfill(loan) for loan in request_cart_to_modify.cart_loans.all()]
    return not(False in disbursements or False in loans or False in backfills) and can_modify_cart_status(request_cart_to_modify)


def subtract_item(request):
    item = get_or_not_found(Item, pk=request.item.id)  # get item object based on item ID
    item.quantity = item.quantity - request.quantity
    item.save()


def approve_deny_cancel_backfill(loan, approve_deny_cancel):
    backfills_requested = loan.backfill_loan.filter(status='backfill_request').all()
    for backfill in backfills_requested:
        backfill.status = approve_deny_cancel
        backfill.save()


def approve_deny_cancel_backfills_in_cart(request_cart_to_modify, approve_deny_cancel):
    [approve_deny_cancel_backfill(loan, approve_deny_cancel) for loan in request_cart_to_modify.cart_loans.all()]


def subtract_item_in_cart(request_cart_to_modify):
    [subtract_item(request) for request in request_cart_to_modify.cart_disbursements.all()]
    [subtract_item(request) for request in request_cart_to_modify.cart_loans.all()]


def start_loan(request):
    for loan in request.cart_loans.all():
        loan.loaned_timestamp = datetime.now()
        loan.save()


def can_convert_request_type(cart, is_staff, request_type):
    return (cart.status == 'active') or (is_staff
                                         and ((cart.status == 'outstanding')
                                              or (cart.status in ('approved', 'fulfilled')
                                                  and request_type == 'loan')))


def get_backfill_quantity(backfill_loan):
    if backfill_loan.filter(status='backfill_request').exists():
        counter = 0
        for backfill in backfill_loan.filter(status='backfill_request'):
            counter = counter + backfill.quantity
        return counter
    return 0


def validate_quantity(request, quantity, request_type):
    max_quantity = request.quantity - request.returned_quantity if request_type == 'loan' else request.quantity
    if quantity is None:
        return max_quantity, True
    if quantity > max_quantity:
        raise ParseError(detail="Quantity requested, {quantity} does not validate with maximum quantity, {max_quantity}"
                         .format(quantity=quantity, max_quantity=max_quantity))
    if request_type == 'loan' and get_backfill_quantity(request.backfill_loan) > (request.quantity - quantity):
        raise ParseError(detail="Cannot convert when backfill quantity {backtill_quantity} is greater than requested"
                                " quantity, {quantity}".format(backtill_quantity=get_backfill_quantity(request
                                                                                                       .backfill_loan),
                                                               quantity=quantity))
    return quantity, quantity == max_quantity


def delete_or_update_request_logic(delete_request_type, old_type, request_type, quantity):
    if delete_request_type and ((old_type == 'disbursement' and request_type.cart.status != 'fulfilled')
                                or (old_type == 'loan' and request_type.returned_quantity == 0)):
        request_type.delete()
    else:
        request_type.quantity = request_type.quantity - quantity
        if old_type == 'loan' and request_type.returned_quantity == request_type.quantity:
            request_type.returned_timestamp = datetime.now()
        request_type.save()


def raise_error_if_bad_quantity_loan(loan):
    for asset in loan.assets.all():
        if asset.item != loan.item:
            raise MethodNotAllowed(detail='This asset {item} does not match loan item {loan_item}'
                                   .format(item=asset.item.name, loan_item=loan.item),
                                   method=raise_error_if_bad_quantity_loan)
    if loan.quantity != Asset.objects.filter(loan=loan).count():
        raise MethodNotAllowed(detail='Quantity does not match', method=raise_error_if_bad_quantity_loan)


def raise_error_if_bad_quantity_disbursement(disbursement):
    for asset in disbursement.assets.all():
        if asset.item != disbursement.item:
            raise MethodNotAllowed(detail='This asset {item} does not match disbursement item {loan_item}'
                                   .format(item=asset.item.name, loan_item=disbursement.item),
                                   method=raise_error_if_bad_quantity_disbursement)
    if disbursement.quantity != Asset.objects.filter(disbursement=disbursement).count():
        raise MethodNotAllowed(detail='Quantity does not match', method=raise_error_if_bad_quantity_loan)


def precheck_asset_item(request_cart):
    asset_loans = request_cart.cart_loans.filter(item__is_asset=True)
    asset_disbursement = request_cart.cart_disbursements.filter(item__is_asset=True)
    [raise_error_if_bad_quantity_loan(loan) for loan in asset_loans]
    [raise_error_if_bad_quantity_disbursement(disbursement) for disbursement in asset_disbursement]


def update_asset_request_type(asset, new_request):
    if not asset:
        return
    if type(new_request) == Loan:
        asset.disbursement = None
        asset.loan = new_request
    else:
        asset.loan = None
        asset.disbursement = new_request
    asset.save()
