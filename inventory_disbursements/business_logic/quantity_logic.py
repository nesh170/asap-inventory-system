from rest_framework.exceptions import ParseError, MethodNotAllowed


def quantity_logic(quantity, item_quantity, method):
    if quantity is None:
        raise ParseError("Quantity must be specified")
    if quantity == 0:
        raise ParseError("Quantity cannot be 0")
    if item_quantity < quantity:
        detail = "Quantity disbursed {disbursed} cannot be greater than item quantity, {item_quantity}".format
        raise MethodNotAllowed(detail=detail(disbursed=quantity,item_quantity=item_quantity),
                               method=method)

