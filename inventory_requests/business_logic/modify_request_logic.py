from django.http import Http404
from items.models import Item
def get_item(pk):
        try:
            return Item.objects.get(pk=pk)
        except Item.DoesNotExist:
            raise Http404

def can_approve_deny_cancel_request(request_to_modify):
        item = get_item(request_to_modify.item.id)
        if (item.quantity - request_to_modify.quantity < 0):
            return False
        return request_to_modify.status == "outstanding"

def approve_request(request_to_modify):
        item = get_item(request_to_modify.item.id)  # get item object based on item ID
        updated_quantity = item.quantity - request_to_modify.quantity
        item.quantity = updated_quantity
        item.save()

def cancel_request(request_to_modify):
    request_to_modify.status = "cancelled"
    request_to_modify.save()

