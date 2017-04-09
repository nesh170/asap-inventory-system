import json
from datetime import datetime, timezone, timedelta

from django.contrib.auth.models import User
from django.urls import reverse
from oauth2_provider.admin import Application
from oauth2_provider.models import AccessToken
from rest_framework import status
from rest_framework.test import APITestCase

from inventory_requests.models import RequestCart
from items.models.asset_models import Asset
from items.models.item_models import Item

ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'password'
BASIC_USER = 'plebian'
BASIC_PASSWORD = 'password'


def equal_asset(test_client, json_asset, asset_id):
    asset = Asset.objects.get(pk=asset_id)
    test_client.assertEqual(json_asset['asset_tag'], asset.asset_tag)
    test_client.assertEqual(json_asset['item_id'], asset.item.id)
    if asset.loan:
        test_client.assertEqual(json_asset['loan']['id'], asset.loan.id)
    if asset.disbursement:
        test_client.assertEqual(json_asset['disbursement']['id'], asset.disbursement.id)


class GetAssetAPI(APITestCase):
    fixtures = ['item_action.json']

    def setUp(self):
        self.admin = User.objects.create_superuser(ADMIN_USERNAME, '', ADMIN_PASSWORD)
        self.application = Application(
            name="Test Application",
            redirect_uris="http://localhost",
            user=self.admin,
            client_type=Application.CLIENT_CONFIDENTIAL,
            authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
        )
        self.application.save()
        self.tok = AccessToken.objects.create(
            user=self.admin, token='1234567890',
            application=self.application, scope='read write',
            expires=datetime.now(timezone.utc) + timedelta(days=30)
        )
        item = Item.objects.create(name='test', quantity=5, is_asset=True)
        item_1 = Item.objects.create(name='polar', quantity=3, is_asset=True)

    def test_get_fields(self):
        url = reverse('asset-list')
        self.client.force_authenticate(user=self.admin, token=self.tok)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json_asset_list = json.loads(str(response.content, 'utf-8'))['results']
        self.assertEqual(json.loads(str(response.content, 'utf-8'))['count'], Asset.objects.count())
        [equal_asset(self, json_asset, json_asset['id']) for json_asset in json_asset_list]


class CreateAssetAPI(APITestCase):
    fixtures = ['item_action.json']

    def setUp(self):
        self.admin = User.objects.create_superuser(ADMIN_USERNAME, '', ADMIN_PASSWORD)
        self.application = Application(
            name="Test Application",
            redirect_uris="http://localhost",
            user=self.admin,
            client_type=Application.CLIENT_CONFIDENTIAL,
            authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
        )
        self.application.save()
        self.tok = AccessToken.objects.create(
            user=self.admin, token='1234567890',
            application=self.application, scope='read write',
            expires=datetime.now(timezone.utc) + timedelta(days=30)
        )

    def test_create_asset_item_id_not_found_fail(self):
        url = reverse('asset-list')
        self.client.force_authenticate(user=self.admin, token=self.tok)
        data = {'item_id': 9000}
        response = self.client.post(path=url, data=data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(json.loads((str(response.content, 'utf-8')))['detail'], 'Item not found')

    def test_create_asset(self):
        url = reverse('asset-list')
        self.client.force_authenticate(user=self.admin, token=self.tok)
        item = Item.objects.create(name='tikna', quantity=5, is_asset=True)
        data = {'item_id': item.id}
        response = self.client.post(path=url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        updated_item = Item.objects.get(pk=item.id)
        self.assertEqual(updated_item.quantity, item.quantity + 1)
        json_asset = json.loads(str(response.content, 'utf-8'))
        equal_asset(self, json_asset, json_asset['id'])
        item.delete()


class UpdateAssetAPI(APITestCase):
    fixtures = ['item_action.json']

    def setUp(self):
        self.admin = User.objects.create_superuser(ADMIN_USERNAME, '', ADMIN_PASSWORD)
        self.application = Application(
            name="Test Application",
            redirect_uris="http://localhost",
            user=self.admin,
            client_type=Application.CLIENT_CONFIDENTIAL,
            authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
        )
        self.application.save()
        self.tok = AccessToken.objects.create(
            user=self.admin, token='1234567890',
            application=self.application, scope='read write',
            expires=datetime.now(timezone.utc) + timedelta(days=30)
        )

    def test_update_asset_tag_not_unique_fail(self):
        item = Item.objects.create(name='unique1', quantity=2, is_asset=True)
        asset_1 = item.assets.first()
        asset_2 = item.assets.exclude(asset_tag=asset_1.asset_tag).first()
        data = {'asset_tag': asset_2.asset_tag}
        url = reverse(viewname='asset-detail', kwargs={'pk': asset_1.id})
        self.client.force_authenticate(user=self.admin, token=self.tok)
        response = self.client.patch(path=url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(str(response.content, 'utf-8'))['asset_tag'],
                         ['asset with this asset tag already exists.'])
        item.delete()

    def test_update_asset_tag(self):
        item = Item.objects.create(name='unique1', quantity=2, is_asset=True)
        asset_1 = item.assets.first()
        data = {'asset_tag': 'RIP'}
        url = reverse(viewname='asset-detail', kwargs={'pk': asset_1.id})
        self.client.force_authenticate(user=self.admin, token=self.tok)
        response = self.client.patch(path=url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json_asset = json.loads(str(response.content, 'utf-8'))
        self.assertEqual(json_asset['asset_tag'], data['asset_tag'])
        equal_asset(self, json_asset, json_asset['id'])
        item.delete()

    def test_update_asset_both_disbursement_loan_fail(self):
        item = Item.objects.create(name='unique1', quantity=1, is_asset=True)
        cart = RequestCart.objects.create(owner=self.admin, reason="test shopping cart", status="outstanding")
        loan = cart.cart_loans.create(item=item, quantity=1)
        disbursement = cart.cart_disbursements.create(item=item, quantity=1)
        asset = item.assets.first()
        data = {'loan_id': loan.id, "disbursement_id": disbursement.id}
        self.client.force_authenticate(user=self.admin, token=self.tok)
        url = reverse(viewname='asset-detail', kwargs={'pk': asset.id})
        response = self.client.patch(path=url, data=data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(json.loads(str(response.content, 'utf-8'))['detail'],
                         'Cannot put in both disbursement and loan')
        item.delete()
        cart.delete()

    def test_update_asset_disbursement(self):
        item = Item.objects.create(name='unique1', quantity=1, is_asset=True)
        cart = RequestCart.objects.create(owner=self.admin, reason="test shopping cart", status="outstanding")
        disbursement = cart.cart_disbursements.create(item=item, quantity=1)
        asset = item.assets.first()
        data = {"disbursement_id": disbursement.id}
        self.client.force_authenticate(user=self.admin, token=self.tok)
        url = reverse(viewname='asset-detail', kwargs={'pk': asset.id})
        response = self.client.patch(path=url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json_asset = json.loads(str(response.content, 'utf-8'))
        equal_asset(self, json_asset, json_asset['id'])
        item.delete()
        cart.delete()

    def test_update_asset_loan(self):
        item = Item.objects.create(name='unique1', quantity=1, is_asset=True)
        cart = RequestCart.objects.create(owner=self.admin, reason="test shopping cart", status="outstanding")
        loan = cart.cart_loans.create(item=item, quantity=1)
        asset = item.assets.first()
        data = {"loan_id": loan.id}
        self.client.force_authenticate(user=self.admin, token=self.tok)
        url = reverse(viewname='asset-detail', kwargs={'pk': asset.id})
        response = self.client.patch(path=url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json_asset = json.loads(str(response.content, 'utf-8'))
        equal_asset(self, json_asset, json_asset['id'])
        item.delete()
        cart.delete()


class DeleteAssetAPI(APITestCase):
    fixtures = ['item_action.json']

    def setUp(self):
        self.admin = User.objects.create_superuser(ADMIN_USERNAME, '', ADMIN_PASSWORD)
        self.application = Application(
            name="Test Application",
            redirect_uris="http://localhost",
            user=self.admin,
            client_type=Application.CLIENT_CONFIDENTIAL,
            authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
        )
        self.application.save()
        self.tok = AccessToken.objects.create(
            user=self.admin, token='1234567890',
            application=self.application, scope='read write',
            expires=datetime.now(timezone.utc) + timedelta(days=30)
        )

    def test_delete_asset(self):
        item = Item.objects.create(name='unique1', quantity=2, is_asset=True)
        asset = item.assets.first()
        self.client.force_authenticate(user=self.admin, token=self.tok)
        url = reverse(viewname='asset-detail', kwargs={'pk': asset.id})
        response = self.client.delete(path=url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        updated_item = Item.objects.get(pk=item.id)
        self.assertEqual(updated_item.quantity, item.quantity - 1)
        item.delete()


class ErrorAssetAPI(APITestCase):
    fixtures = ['item_action.json']

    def setUp(self):
        self.admin = User.objects.create_superuser(ADMIN_USERNAME, '', ADMIN_PASSWORD)
        self.application = Application(
            name="Test Application",
            redirect_uris="http://localhost",
            user=self.admin,
            client_type=Application.CLIENT_CONFIDENTIAL,
            authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
        )
        self.application.save()
        self.tok = AccessToken.objects.create(
            user=self.admin, token='1234567890',
            application=self.application, scope='read write',
            expires=datetime.now(timezone.utc) + timedelta(days=30)
        )

    def test_fail_log_acquisition(self):
        item = Item.objects.create(name='unique1', quantity=2, is_asset=True)
        self.client.force_authenticate(user=self.admin, token=self.tok)
        data = {'item_id': item.id, 'quantity': 1}
        url = reverse(viewname='item-quantity-modification')
        response = self.client.post(path=url, data=data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(json.loads(str(response.content, 'utf-8'))['detail'],
                         "Cannot modify quantity of is_asset items")


class ModifyItemIsAssetAPI(APITestCase):
    fixtures = ['item_action.json']

    def setUp(self):
        self.admin = User.objects.create_superuser(ADMIN_USERNAME, '', ADMIN_PASSWORD)
        self.application = Application(
            name="Test Application",
            redirect_uris="http://localhost",
            user=self.admin,
            client_type=Application.CLIENT_CONFIDENTIAL,
            authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
        )
        self.application.save()
        self.tok = AccessToken.objects.create(
            user=self.admin, token='1234567890',
            application=self.application, scope='read write',
            expires=datetime.now(timezone.utc) + timedelta(days=30)
        )

    def test_change_item_to_non_asset_fail(self):
        item = Item.objects.create(name='asset_item', quantity=2, is_asset=True)
        url = reverse(viewname='item-detail', kwargs={'pk': item.id})
        data = {'is_asset': False}
        self.client.force_authenticate(user=self.admin, token=self.tok)
        response = self.client.patch(path=url, data=data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(json.loads(str(response.content, 'utf-8'))['detail'],
                         "This Item is already an Asset")

    def test_change_item_quantity_when_asset_fail(self):
        item = Item.objects.create(name='asset_item', quantity=2, is_asset=True)
        url = reverse(viewname='item-detail', kwargs={'pk': item.id})
        data = {'quantity': 10}
        self.client.force_authenticate(user=self.admin, token=self.tok)
        response = self.client.patch(path=url, data=data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(json.loads(str(response.content, 'utf-8'))['detail'],
                         "Cannot change quantity if Item is an Asset")

    def test_item_to_asset(self):
        item = Item.objects.create(name='item_asset', quantity=10)
        url = reverse(viewname='item-detail', kwargs={'pk': item.id})
        data = {'is_asset': True}
        self.client.force_authenticate(user=self.admin, token=self.tok)
        response = self.client.patch(path=url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(item.assets.count(), item.quantity)


















