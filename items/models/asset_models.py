from django.db import models

from inventory_requests.models import Loan, Disbursement
from items.models.item_models import Item

ASSET_TAG_MAX_LENGTH = 40


class Asset(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='assets')
    asset_tag = models.CharField(max_length=ASSET_TAG_MAX_LENGTH, unique=True)
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name='assets', null=True)
    disbursement = models.ForeignKey(Disbursement, on_delete=models.CASCADE, related_name='assets', null=True)

    def is_valid(self):
        return not(self.loan and self.disbursement)





