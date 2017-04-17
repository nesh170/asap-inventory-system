# username and password to create superuser for testing
import json
from datetime import datetime, timezone, timedelta

from django.contrib.auth.models import User
from django.urls import reverse
from oauth2_provider.admin import Application
from oauth2_provider.models import AccessToken
from oauth2_provider.settings import oauth2_settings
from rest_framework import status
from rest_framework.test import APITestCase

from inventory_requests.models import RequestCart, Loan
from items.models.asset_models import Asset

from items.models.item_models import Item

USERNAME = 'admin'
PASSWORD = 'adminPassword'
TEST_USERNAME = 'test_user'
TEST_PASSWORD = 'testPassword'


def equal_loans(test_client, loan_json, loan_id, cart_id=None):
    loan = Loan.objects.get(pk=loan_id)
    test_client.assertEqual(loan_json.get('item').get('name'), loan.item.name)
    test_client.assertEqual(loan_json.get('quantity'), loan.quantity)
    test_client.assertEqual(loan_json.get('cart_id'), loan.cart.id)
    if cart_id is not None:
        test_client.assertEqual(loan_json.get('cart_id'), cart_id)
        test_client.assertEqual(loan.cart.id, cart_id)


class LoansTestCases(APITestCase):
    fixtures = ['requests_action.json', 'email_templates.json']

    def setUp(self):
        self.admin = User.objects.create_superuser(USERNAME, '', PASSWORD)
        self.basic_user = User.objects.create_user(TEST_USERNAME, '', TEST_PASSWORD)
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
        self.test_application = Application(
            name="Test User Application",
            redirect_uris="http://localhost",
            user=self.basic_user,
            client_type=Application.CLIENT_CONFIDENTIAL,
            authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
        )
        self.test_application.save()
        self.test_tok = AccessToken.objects.create(
            user=self.basic_user, token='123490',
            application=self.test_application, scope='read write',
            expires=datetime.now(timezone.utc) + timedelta(days=30)
        )
        oauth2_settings._DEFAULT_SCOPES = ['read', 'write', 'groups']
        self.item = Item.objects.create(name="test_item_1", quantity=10)
        self.item_1 = Item.objects.create(name="test item 2", quantity=4)

    def test_get_all_loans(self):
        cart = RequestCart.objects.create(owner=self.basic_user, reason="test shopping cart")
        cart.cart_loans.create(item=self.item, quantity=2)
        cart.cart_loans.create(item=self.item_1, quantity=4)
        url = reverse('add-loan-to-cart')
        self.client.force_authenticate(user=self.admin, token=self.tok)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(str(response.content, 'utf-8'))['count'], Loan.objects.count())
        loans_json = json.loads(str(response.content, 'utf-8'))['results']
        [equal_loans(self, loan_json, loan_json['id']) for loan_json in loans_json]
        cart.delete()

    def test_create_loan_fail_inactive_cart(self):
        cart = RequestCart.objects.create(owner=self.basic_user, status='fulfilled', reason="test")
        self.client.force_authenticate(user=self.basic_user, token=self.test_tok)
        url = reverse('add-loan-to-cart')
        data = {'item_id': self.item.id, 'quantity': 10}
        response = self.client.post(path=url, data=data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(json.loads(str(response.content, 'utf-8'))['detail'], "Item must be added to active cart")
        cart.delete()

    def test_create_loan(self):
        cart = RequestCart.objects.create(owner=self.basic_user, reason="test shopping cart")
        self.client.force_authenticate(user=self.basic_user, token=self.test_tok)
        url = reverse('add-loan-to-cart')
        data = {'item_id':self.item.id, 'quantity': 10}
        response = self.client.post(path=url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        loan_json = json.loads(str(response.content, 'utf-8'))
        equal_loans(test_client=self, loan_json=loan_json, loan_id=loan_json['id'], cart_id=cart.id)
        cart.delete()

    def test_delete_loan_inactive_cart(self):
        cart = RequestCart.objects.create(owner=self.basic_user, status='fulfilled', reason="test")
        loan = Loan.objects.create(item=self.item_1, quantity=10, cart=cart)
        self.client.force_authenticate(user=self.basic_user, token=self.test_tok)
        url = reverse('delete-loan-from-cart',  kwargs={'pk': str(loan.id)})
        response = self.client.delete(path=url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(json.loads(str(response.content, 'utf-8'))['detail'],
                         "Cannot delete loan as request status: fulfilled != active")
        self.assertTrue(Loan.objects.filter(pk=loan.id).exists())

    def test_delete_loan(self):
        cart = RequestCart.objects.create(owner=self.basic_user, reason="active cart is lit")
        loan = Loan.objects.create(item=self.item_1, quantity=10, cart=cart)
        self.client.force_authenticate(user=self.basic_user, token=self.test_tok)
        url = reverse('delete-loan-from-cart',  kwargs={'pk': str(loan.id)})
        response = self.client.delete(path=url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Loan.objects.filter(pk=loan.id).exists())
        cart.delete()

    def test_return_loan_unfulfilled_cart(self):
        cart = RequestCart.objects.create(owner=self.basic_user, status='active', reason="test")
        loan = Loan.objects.create(item=self.item_1, quantity=4, cart=cart, loaned_timestamp=datetime.now())
        self.client.force_authenticate(user=self.admin, token=self.tok)
        url = reverse('return-loan-from-cart', kwargs={'pk': str(loan.id)})
        response = self.client.patch(path=url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        detail_str = "Request needs to be fulfilled but is {status} and {item_name} cannot be " \
                     "returned already by {user_name} and returned loan quantity is {returned_quantity} " \
                     "and quantity is {quantity}"\
            .format(status=cart.status, item_name=self.item_1.name, user_name=self.basic_user.username,
                    returned_quantity=loan.returned_quantity, quantity=loan.quantity)
        self.assertEqual(json.loads(str(response.content, 'utf-8'))['detail'], detail_str)
        self.assertTrue(Loan.objects.filter(pk=loan.id).exists())
        cart.delete()

    def test_return_loan(self):
        cart = RequestCart.objects.create(owner=self.basic_user, status="fulfilled", reason="return loan cart")
        loan = Loan.objects.create(item=self.item_1, quantity=4, cart=cart, loaned_timestamp=datetime.now())
        self.item_1.quantity = self.item_1.quantity - loan.quantity
        self.item_1.save()
        self.client.force_authenticate(user=self.admin, token=self.tok)
        url = reverse('return-loan-from-cart', kwargs={'pk': str(loan.id)})
        response = self.client.patch(path=url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        loan_json = json.loads(str(response.content, 'utf-8'))
        equal_loans(test_client=self, loan_json=loan_json, loan_id=loan_json['id'])
        updated_loan = Loan.objects.get(pk=loan.id)
        updated_item = Item.objects.get(pk=self.item_1.id)
        self.assertEqual(updated_item.quantity, self.item_1.quantity + loan.quantity)
        self.assertIsNotNone(updated_loan.returned_timestamp)
        self.assertTrue(updated_loan.returned_timestamp > updated_loan.loaned_timestamp)
        self.assertEqual(updated_loan.returned_quantity, updated_loan.quantity)
        cart.delete()

    def test_return_partial_loan(self):
        cart = RequestCart.objects.create(owner=self.basic_user, status="fulfilled", reason="return loan cart")
        loan = Loan.objects.create(item=self.item_1, quantity=4, cart=cart, loaned_timestamp=datetime.now())
        data = {'quantity': 1}
        self.item_1.quantity = self.item_1.quantity - loan.quantity
        self.item_1.save()
        self.client.force_authenticate(user=self.admin, token=self.tok)
        url = reverse('return-loan-from-cart', kwargs={'pk': str(loan.id)})
        response = self.client.patch(path=url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        loan_json = json.loads(str(response.content, 'utf-8'))
        equal_loans(test_client=self, loan_json=loan_json, loan_id=loan_json['id'])
        updated_loan = Loan.objects.get(pk=loan.id)
        updated_item = Item.objects.get(pk=self.item_1.id)
        self.assertEqual(updated_item.quantity, self.item_1.quantity + data['quantity'])
        self.assertEqual(updated_loan.returned_quantity, data['quantity'])
        cart.delete()

    def test_return_partial_loan_when_all_returned(self):
        cart = RequestCart.objects.create(owner=self.basic_user, status="fulfilled", reason="return loan cart")
        loan = Loan.objects.create(item=self.item_1, quantity=4, cart=cart, loaned_timestamp=datetime.now(),
                                   returned_quantity=2)
        data = {'quantity': 2}
        self.item_1.quantity = self.item_1.quantity - loan.quantity
        self.item_1.save()
        self.client.force_authenticate(user=self.admin, token=self.tok)
        url = reverse('return-loan-from-cart', kwargs={'pk': str(loan.id)})
        response = self.client.patch(path=url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        loan_json = json.loads(str(response.content, 'utf-8'))
        equal_loans(test_client=self, loan_json=loan_json, loan_id=loan_json['id'])
        updated_loan = Loan.objects.get(pk=loan.id)
        updated_item = Item.objects.get(pk=self.item_1.id)
        self.assertEqual(updated_item.quantity, self.item_1.quantity + updated_loan.returned_quantity)
        self.assertEqual(updated_loan.quantity, updated_loan.returned_quantity)
        self.assertTrue(updated_loan.returned_timestamp is not None)
        cart.delete()

    def test_return_partial_loan_with_quantity_return_zero(self):
        cart = RequestCart.objects.create(owner=self.basic_user, status="fulfilled", reason="return loan cart")
        loan = Loan.objects.create(item=self.item_1, quantity=4, cart=cart, loaned_timestamp=datetime.now())
        data = {'quantity': 0}
        self.client.force_authenticate(user=self.admin, token=self.tok)
        url = reverse('return-loan-from-cart', kwargs={'pk': str(loan.id)})
        response = self.client.patch(path=url, data=data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual("Quantity {quantity} cannot be greater than loan quantity({loan_q}) or less than 1"
                         .format(quantity=data['quantity'], loan_q=loan.quantity),
                         json.loads(str(response.content, 'utf-8'))['detail'])

    def test_return_partial_loan_when_some_returned(self):
        cart = RequestCart.objects.create(owner=self.basic_user, status="fulfilled", reason="return loan cart")
        loan = Loan.objects.create(item=self.item_1, quantity=4, cart=cart, loaned_timestamp=datetime.now(),
                                   returned_quantity=1)
        data = {'quantity': 2}
        self.item_1.quantity = self.item_1.quantity - loan.quantity + loan.returned_quantity
        self.item_1.save()
        self.client.force_authenticate(user=self.admin, token=self.tok)
        url = reverse('return-loan-from-cart', kwargs={'pk': str(loan.id)})
        response = self.client.patch(path=url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        loan_json = json.loads(str(response.content, 'utf-8'))
        equal_loans(test_client=self, loan_json=loan_json, loan_id=loan_json['id'])
        updated_loan = Loan.objects.get(pk=loan.id)
        updated_item = Item.objects.get(pk=self.item_1.id)
        self.assertEqual(updated_item.quantity, self.item_1.quantity + updated_loan.returned_quantity
                         - loan.returned_quantity)
        self.assertEqual(loan.returned_quantity + data['quantity'], updated_loan.returned_quantity)
        self.assertTrue(updated_loan.returned_timestamp is None)
        cart.delete()

    def test_return_partial_loan_when_all_returned_fail_high_quantity(self):
        cart = RequestCart.objects.create(owner=self.basic_user, status="fulfilled", reason="return loan cart")
        loan = Loan.objects.create(item=self.item_1, quantity=4, cart=cart, loaned_timestamp=datetime.now(),
                                   returned_quantity=2)
        data = {'quantity': 3}
        self.client.force_authenticate(user=self.admin, token=self.tok)
        url = reverse('return-loan-from-cart', kwargs={'pk': str(loan.id)})
        response = self.client.patch(path=url, data=data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        detail_str = "Request needs to be fulfilled but is {status} and {item_name} cannot be " \
                     "returned already by {user_name} and returned loan quantity is {returned_quantity} " \
                     "and quantity is {quantity}"\
            .format(status=cart.status, item_name=self.item_1.name, user_name=self.basic_user.username,
                    returned_quantity=loan.returned_quantity, quantity=loan.quantity)
        self.assertEqual(json.loads(str(response.content, 'utf-8'))['detail'], detail_str)
        cart.delete()

    def test_return_all_loans_fully_returned_fail(self):
        cart = RequestCart.objects.create(owner=self.basic_user, status="fulfilled", reason="return loan cart")
        loan = Loan.objects.create(item=self.item, quantity=1, cart=cart, loaned_timestamp=datetime.now(),
                                   returned_timestamp=datetime.now())
        self.item.quantity = self.item.quantity - loan.quantity
        self.item.save()
        self.client.force_authenticate(user=self.admin, token=self.tok)
        url = reverse('return-all-loans-from-cart', kwargs={'pk': str(cart.id)})
        response = self.client.patch(path=url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(json.loads(str(response.content, 'utf-8'))['detail'],
                         "Request needs to be fulfilled but is fulfilled or Cart has been fully returned")

    def test_return_all_loans(self):
        cart = RequestCart.objects.create(owner=self.basic_user, status="fulfilled", reason="return loan cart")
        loan = Loan.objects.create(item=self.item, quantity=1, cart=cart, loaned_timestamp=datetime.now())
        loan_1 = Loan.objects.create(item=self.item_1, quantity=4, cart=cart, loaned_timestamp=datetime.now())
        self.item.quantity = self.item.quantity - loan.quantity
        self.item.save()
        self.item_1.quantity = self.item_1.quantity - loan_1.quantity
        self.item_1.save()
        self.client.force_authenticate(user=self.admin, token=self.tok)
        url = reverse('return-all-loans-from-cart', kwargs={'pk': str(cart.id)})
        response = self.client.patch(path=url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        cart_id = json.loads(str(response.content, 'utf-8'))['id']
        loans_json = json.loads(str(response.content, 'utf-8'))['cart_loans']
        [equal_loans(test_client=self, loan_json=loan_json, loan_id=loan_json['id'], cart_id=cart_id)
         for loan_json in loans_json]
        [self.assertTrue(Loan.objects.get(pk=loan_json['id']).returned_timestamp is not None)
         for loan_json in loans_json]
        [self.assertTrue(Loan.objects.get(pk=loan_json['id']).returned_quantity,
                         Loan.objects.get(pk=loan_json['id']).quantity) for loan_json in loans_json]
        cart.delete()


class CartAssetAPI(APITestCase):
    fixtures = ['requests_action.json', 'email_templates.json']

    def setUp(self):
        self.admin = User.objects.create_superuser(USERNAME, '', PASSWORD)
        self.basic_user = User.objects.create_user(TEST_USERNAME, '', TEST_PASSWORD)
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

    def test_admin_cart_loan_not_asset_marked_fail(self):
        request_cart = RequestCart.objects.create(status="active", reason="test shopping cart",
                                                  staff_comment="this is an admin comment", staff=self.admin)
        item = Item.objects.create(name='test_item', quantity=10, is_asset=True)
        request_cart.cart_loans.create(item=item, quantity=1)
        url = reverse('dispense-request-cart', kwargs={'pk': str(request_cart.id)})
        data = {'owner_id': self.basic_user.id, 'staff_comment': 'lit'}
        self.client.force_authenticate(user=self.admin, token=self.tok)
        response = self.client.patch(path=url, data=data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(json.loads(str(response.content, 'utf-8'))['detail']
                         , "Quantity does not match")
        item.delete()
        request_cart.delete()

    def test_admin_cart_loan_asset_marked(self):
        request_cart = RequestCart.objects.create(status="active", reason="test shopping cart",
                                                  staff_comment="this is an admin comment", staff=self.admin)
        item = Item.objects.create(name='test_item', quantity=1, is_asset=True)
        loan = request_cart.cart_loans.create(item=item, quantity=1)
        Asset.objects.create(item=item, loan=loan)
        url = reverse('dispense-request-cart', kwargs={'pk': str(request_cart.id)})
        data = {'owner_id': self.basic_user.id, 'staff_comment': 'lit'}
        self.client.force_authenticate(user=self.admin, token=self.tok)
        response = self.client.patch(path=url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_item = Item.objects.get(pk=item.id)
        self.assertEqual(updated_item.quantity, item.quantity - loan.quantity)
        item.delete()
        request_cart.delete()

    def test_return_loan(self):
        request_cart = RequestCart.objects.create(owner=self.basic_user, status="fulfilled",
                                                  reason="test shopping cart",
                                                  staff_comment="this is an admin comment", staff=self.admin)
        item = Item.objects.create(name='test_item', quantity=2, is_asset=True)
        loan = request_cart.cart_loans.create(item=item, quantity=1, loaned_timestamp=datetime.now())
        asset = item.assets.first()
        asset.loan = loan
        asset.save()
        item = Item.objects.get(pk=item.id)
        item.quantity = item.quantity - 1
        item.save()
        url = reverse('return-all-loans-from-cart', kwargs={'pk': str(request_cart.id)})
        self.client.force_authenticate(user=self.admin, token=self.tok)
        response = self.client.patch(path=url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_asset = Asset.objects.get(pk=asset.id)
        self.assertIsNone(updated_asset.loan)
        updated_item = Item.objects.get(pk=item.id)
        self.assertEqual(updated_item.quantity, item.quantity + 1)
        self.assertEqual(updated_item.quantity, Asset.objects.filter(item=updated_item).count())

    def test_return_quantity_asset_loan_fail(self):
        request_cart = RequestCart.objects.create(owner=self.basic_user, status="fulfilled",
                                                  reason="test shopping cart",
                                                  staff_comment="this is an admin comment", staff=self.admin)
        item = Item.objects.create(name='test_item', quantity=2, is_asset=True)
        loan = request_cart.cart_loans.create(item=item, quantity=1, loaned_timestamp=datetime.now())
        asset = item.assets.first()
        asset.loan = loan
        asset.save()
        item = Item.objects.get(pk=item.id)
        item.quantity = item.quantity - 1
        item.save()
        data = {'quantity': 1}
        url = reverse('return-loan-from-cart', kwargs={'pk': str(loan.id)})
        self.client.force_authenticate(user=self.admin, token=self.tok)
        response = self.client.patch(path=url, data=data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(json.loads(str(response.content, 'utf-8'))['detail'], 'Item cannot be an asset')

    def test_return_asset_bad_request_fail(self):
        request_cart = RequestCart.objects.create(owner=self.basic_user, status="fulfilled",
                                                  reason="test shopping cart",
                                                  staff_comment="this is an admin comment", staff=self.admin)
        item = Item.objects.create(name='test_item', quantity=2, is_asset=True)
        loan = request_cart.cart_loans.create(item=item, quantity=1, loaned_timestamp=datetime.now())
        asset = item.assets.first()
        asset.loan = loan
        asset.save()
        item = Item.objects.get(pk=item.id)
        item.quantity = item.quantity - 1
        item.save()
        data = {'quantity': 1}
        url = reverse('return-asset-loan-from-cart', kwargs={'pk': str(loan.id)})
        self.client.force_authenticate(user=self.admin, token=self.tok)
        response = self.client.patch(path=url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(str(response.content, 'utf-8'))['detail'], 'Must have asset_id')

    def test_return_asset(self):
        request_cart = RequestCart.objects.create(owner=self.basic_user, status="fulfilled",
                                                  reason="test shopping cart",
                                                  staff_comment="this is an admin comment", staff=self.admin)
        item = Item.objects.create(name='test_item', quantity=2, is_asset=True)
        loan = request_cart.cart_loans.create(item=item, quantity=1, loaned_timestamp=datetime.now())
        asset = item.assets.first()
        asset.loan = loan
        asset.save()
        item = Item.objects.get(pk=item.id)
        item.quantity = item.quantity - 1
        item.save()
        data = {'asset_id': asset.id}
        url = reverse('return-asset-loan-from-cart', kwargs={'pk': str(loan.id)})
        self.client.force_authenticate(user=self.admin, token=self.tok)
        response = self.client.patch(path=url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_item = Item.objects.get(pk=item.id)
        self.assertEqual(updated_item.quantity, item.quantity + 1)
        updated_loan = Loan.objects.get(pk=loan.id)
        self.assertIsNotNone(updated_loan.returned_timestamp)
        self.assertEqual(loan.quantity, updated_loan.returned_quantity)

    def test_instant_request_loan_asset(self):
        item = Item.objects.create(name='test_item', quantity=2, is_asset=True)
        asset = item.assets.first()
        data = {'current_type': 'loan', 'owner_id': self.basic_user.id, 'asset_id': asset.id}
        url = reverse('instant-request')
        self.client.force_authenticate(user=self.admin, token=self.tok)
        response = self.client.post(path=url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json_cart = json.loads(str(response.content, 'utf-8'))
        cart = RequestCart.objects.get(pk=json_cart['id'])
        loan = cart.cart_loans.first()
        updated_asset = Asset.objects.get(pk=asset.id)
        self.assertEqual(item.quantity - 1, loan.item.quantity)
        self.assertEqual(updated_asset.loan.id, loan.id)

    def test_instant_request_asset_tied_to_loan_already(self):
        request_cart = RequestCart.objects.create(owner=self.basic_user, status="fulfilled",
                                                  reason="test shopping cart",
                                                  staff_comment="this is an admin comment", staff=self.admin)
        item = Item.objects.create(name='test_item', quantity=2, is_asset=True)
        loan = request_cart.cart_loans.create(item=item, quantity=1)
        asset = item.assets.first()
        asset.loan = loan
        asset.save()
        data = {'current_type': 'loan', 'owner_id': self.basic_user.id, 'asset_id': asset.id}
        url = reverse('instant-request')
        self.client.force_authenticate(user=self.admin, token=self.tok)
        response = self.client.post(path=url, data=data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(json.loads(str(response.content, 'utf-8'))['detail'],
                         'Asset is already tied to loan/disbursement')

