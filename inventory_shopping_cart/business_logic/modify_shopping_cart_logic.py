from rest_framework.exceptions import NotFound

from items.models import Item
def get_item(pk):
    try:
        return Item.objects.get(pk=pk)
    except Item.DoesNotExist:
        raise NotFound(detail="Item not Found")

def can_approve_deny_cancel_shopping_cart(shopping_cart_to_modify, modificationType):
    for request in shopping_cart_to_modify.requests.all():
        item = get_item(request.item.id)
        if (item.quantity - request.quantity_requested < 0 and modificationType == "approved"):
            return False
    return shopping_cart_to_modify.status == "outstanding"

def approve_shopping_cart(shopping_cart_to_modify):
    for request in shopping_cart_to_modify.requests.all():
        item = get_item(request.item.id)  # get item object based on item ID
        item.quantity = item.quantity - request.quantity_requested
        item.save()

def cancel_shopping_cart(shopping_cart_to_modify):
    shopping_cart_to_modify.status = "cancelled"
    shopping_cart_to_modify.save()

