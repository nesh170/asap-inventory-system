import json
from datetime import timedelta, timezone, datetime

from django.contrib.auth.models import User
from django.urls import reverse
from oauth2_provider.admin import Application
from oauth2_provider.models import AccessToken
from oauth2_provider.settings import oauth2_settings
from rest_framework import status
from rest_framework.test import APITestCase

from inventory_requests.models import RequestCart, Disbursement, Loan
from items.models import Item

# username and password to create superuser and regular user for testing
USERNAME = 'test'
PASSWORD = 'testPassword'
TEST_USERNAME = 'ankit'
TEST_PASSWORD = 'lol'


class ConvertRequestTypeTestCase(APITestCase):
    fixtures = ['requests_action.json', 'email_templates.json']

    def setUp(self):
        self.admin = User.objects.create_superuser(USERNAME, 'test@test.com', PASSWORD)
        self.receiver = User.objects.create_user(TEST_USERNAME, 'test@test.com', TEST_PASSWORD)
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
        self.receiver_application = Application(
            name="Test Application",
            redirect_uris="http://localhost",
            user=self.receiver,
            client_type=Application.CLIENT_CONFIDENTIAL,
            authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
        )
        self.receiver_application.save()
        self.receiver_tok = AccessToken.objects.create(
            user=self.receiver, token='1234890',
            application=self.receiver_application, scope='read write',
            expires=datetime.now(timezone.utc) + timedelta(days=30)
        )
        oauth2_settings._DEFAULT_SCOPES = ['read', 'write', 'groups']

    def test_active_cart_convert_loan_to_disbursement(self):
        self.client.force_authenticate(user=self.receiver, token=self.receiver_tok)
        item = Item.objects.create(name="test_item", quantity=10)
        cart = RequestCart.objects.create(owner=self.receiver, status="active", reason="lit")
        loan = Loan.objects.create(item=item, cart=cart, quantity=10)
        data = {'current_type': 'loan', 'pk': loan.id}
        url = reverse('convert-request-type')
        response = self.client.post(path=url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response_json = json.loads(str(response.content, 'utf-8'))
        disbursement = Disbursement.objects.get(pk=response_json['id'])
        self.assertEqual(loan.item.name, disbursement.item.name)
        self.assertEqual(loan.quantity, disbursement.quantity)
        self.assertEqual(loan.cart.owner.username, disbursement.cart.owner.username)
        self.assertFalse(Loan.objects.filter(pk=loan.id).exists())
        cart.delete()

    def test_active_cart_convert_disbursement_to_loan(self):
        self.client.force_authenticate(user=self.receiver, token=self.receiver_tok)
        item = Item.objects.create(name="test_item", quantity=10)
        cart = RequestCart.objects.create(owner=self.receiver, status="active", reason="lit")
        disbursement = Disbursement.objects.create(item=item, cart=cart, quantity=10)
        data = {'current_type': 'disbursement', 'pk': disbursement.id}
        url = reverse('convert-request-type')
        response = self.client.post(path=url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response_json = json.loads(str(response.content, 'utf-8'))
        loan = Loan.objects.get(pk=response_json['id'])
        self.assertEqual(loan.item.name, disbursement.item.name)
        self.assertEqual(loan.quantity, disbursement.quantity)
        self.assertEqual(loan.cart.owner.username, disbursement.cart.owner.username)
        self.assertFalse(Disbursement.objects.filter(pk=disbursement.id).exists())
        cart.delete()

    def test_active_cart_convert_disbursement_to_loan_staff(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        item = Item.objects.create(name="test_item11", quantity=10)
        cart = RequestCart.objects.create(owner=self.receiver, status="active", reason="lit")
        disbursement = Disbursement.objects.create(item=item, cart=cart, quantity=10)
        data = {'current_type': 'disbursement', 'pk': disbursement.id}
        url = reverse('convert-request-type')
        response = self.client.post(path=url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response_json = json.loads(str(response.content, 'utf-8'))
        loan = Loan.objects.get(pk=response_json['id'])
        self.assertEqual(loan.item.name, disbursement.item.name)
        self.assertEqual(loan.quantity, disbursement.quantity)
        self.assertEqual(loan.cart.owner.username, disbursement.cart.owner.username)
        self.assertFalse(Disbursement.objects.filter(pk=disbursement.id).exists())
        cart.delete()

    def test_active_cart_convert_loan_to_disbursement_staff(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        item = Item.objects.create(name="test_item128937", quantity=10)
        cart = RequestCart.objects.create(owner=self.receiver, status="active", reason="lit")
        loan = Loan.objects.create(item=item, cart=cart, quantity=10)
        data = {'current_type': 'loan', 'pk': loan.id}
        url = reverse('convert-request-type')
        response = self.client.post(path=url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response_json = json.loads(str(response.content, 'utf-8'))
        disbursement = Disbursement.objects.get(pk=response_json['id'])
        self.assertEqual(loan.item.name, disbursement.item.name)
        self.assertEqual(loan.quantity, disbursement.quantity)
        self.assertEqual(loan.cart.owner.username, disbursement.cart.owner.username)
        self.assertFalse(Loan.objects.filter(pk=loan.id).exists())
        cart.delete()

    def test_outstanding_cart_convert_loan_to_disbursement_staff(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        item = Item.objects.create(name="test_item1289371", quantity=10)
        cart = RequestCart.objects.create(owner=self.receiver, status="outstanding", reason="lit")
        loan = Loan.objects.create(item=item, cart=cart, quantity=10)
        data = {'current_type': 'loan', 'pk': loan.id}
        url = reverse('convert-request-type')
        response = self.client.post(path=url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response_json = json.loads(str(response.content, 'utf-8'))
        disbursement = Disbursement.objects.get(pk=response_json['id'])
        self.assertEqual(loan.item.name, disbursement.item.name)
        self.assertEqual(loan.quantity, disbursement.quantity)
        self.assertEqual(loan.cart.owner.username, disbursement.cart.owner.username)
        self.assertFalse(Loan.objects.filter(pk=loan.id).exists())
        cart.delete()

    def test_outstanding_cart_convert_disbursement_to_loan_staff(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        item = Item.objects.create(name="test_item128937", quantity=10)
        cart = RequestCart.objects.create(owner=self.receiver, status="outstanding", reason="lit")
        disbursement = Disbursement.objects.create(item=item, cart=cart, quantity=10)
        data = {'current_type': 'disbursement', 'pk': disbursement.id}
        url = reverse('convert-request-type')
        response = self.client.post(path=url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response_json = json.loads(str(response.content, 'utf-8'))
        loan = Loan.objects.get(pk=response_json['id'])
        self.assertEqual(loan.item.name, disbursement.item.name)
        self.assertEqual(loan.quantity, disbursement.quantity)
        self.assertEqual(loan.cart.owner.username, disbursement.cart.owner.username)
        self.assertFalse(Disbursement.objects.filter(pk=disbursement.id).exists())
        cart.delete()

    def test_approved_cart_convert_loan_to_disbursement_staff(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        item = Item.objects.create(name="test_item128937", quantity=10)
        cart = RequestCart.objects.create(owner=self.receiver, status="approved", reason="lit")
        loan = Loan.objects.create(item=item, cart=cart, quantity=10)
        data = {'current_type': 'loan', 'pk': loan.id}
        url = reverse('convert-request-type')
        response = self.client.post(path=url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response_json = json.loads(str(response.content, 'utf-8'))
        disbursement = Disbursement.objects.get(pk=response_json['id'])
        self.assertEqual(loan.item.name, disbursement.item.name)
        self.assertEqual(loan.quantity, disbursement.quantity)
        self.assertEqual(loan.cart.owner.username, disbursement.cart.owner.username)
        self.assertFalse(Loan.objects.filter(pk=loan.id).exists())
        cart.delete()

    def test_approved_cart_convert_disbursement_to_loan_staff_fail(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        item = Item.objects.create(name="test_item128937", quantity=10)
        cart = RequestCart.objects.create(owner=self.receiver, status="approved", reason="lit")
        disbursement = Disbursement.objects.create(item=item, cart=cart, quantity=10)
        data = {'current_type': 'disbursement', 'pk': disbursement.id}
        url = reverse('convert-request-type')
        response = self.client.post(path=url, data=data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(json.loads(str(response.content, 'utf-8'))['detail'],
                         "Cannot change request_type due to cart_status {status}".format(status=cart.status))
        cart.delete()

    def test_fulfilled_cart_convert_loan_to_disbursement_staff(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        item = Item.objects.create(name="test_item128937", quantity=10)
        cart = RequestCart.objects.create(owner=self.receiver, status="fulfilled", reason="lit")
        loan = Loan.objects.create(item=item, cart=cart, quantity=10)
        data = {'current_type': 'loan', 'pk': loan.id}
        url = reverse('convert-request-type')
        response = self.client.post(path=url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response_json = json.loads(str(response.content, 'utf-8'))
        disbursement = Disbursement.objects.get(pk=response_json['id'])
        self.assertEqual(loan.item.name, disbursement.item.name)
        self.assertEqual(loan.quantity, disbursement.quantity)
        self.assertEqual(loan.cart.owner.username, disbursement.cart.owner.username)
        self.assertFalse(Loan.objects.filter(pk=loan.id).exists())
        cart.delete()

    def test_fulfilled_cart_convert_disbursement_to_loan_staff_fail(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        item = Item.objects.create(name="test_item128937", quantity=10)
        cart = RequestCart.objects.create(owner=self.receiver, status="fulfilled", reason="lit")
        disbursement = Disbursement.objects.create(item=item, cart=cart, quantity=10)
        data = {'current_type': 'disbursement', 'pk': disbursement.id}
        url = reverse('convert-request-type')
        response = self.client.post(path=url, data=data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(json.loads(str(response.content, 'utf-8'))['detail'],
                         "Cannot change request_type due to cart_status {status}".format(status=cart.status))
        cart.delete()

    def test_outstanding_cart_convert_loan_to_disbursement_staff_quantity_less_1_fail(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        item = Item.objects.create(name="test_item1289371", quantity=10)
        cart = RequestCart.objects.create(owner=self.receiver, status="outstanding", reason="lit")
        loan = Loan.objects.create(item=item, cart=cart, quantity=10)
        data = {'current_type': 'loan', 'pk': loan.id, 'quantity': 0}
        url = reverse('convert-request-type')
        response = self.client.post(path=url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(str(response.content, 'utf-8'))['quantity'][0],
                         'Ensure this value is greater than or equal to 1.')

    def test_fulfilled_cart_convert_loan_to_disbursement_staff_quantity_equal_max_value_no_returned(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        item = Item.objects.create(name="test_item128937", quantity=10)
        cart = RequestCart.objects.create(owner=self.receiver, status="fulfilled", reason="lit")
        loan = Loan.objects.create(item=item, cart=cart, quantity=10)
        data = {'current_type': 'loan', 'pk': loan.id, 'quantity': loan.quantity - loan.returned_quantity}
        url = reverse('convert-request-type')
        response = self.client.post(path=url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response_json = json.loads(str(response.content, 'utf-8'))
        disbursement = Disbursement.objects.get(pk=response_json['id'])
        self.assertEqual(loan.item.name, disbursement.item.name)
        self.assertEqual(loan.quantity, disbursement.quantity)
        self.assertEqual(loan.cart.owner.username, disbursement.cart.owner.username)
        self.assertFalse(Loan.objects.filter(pk=loan.id).exists())
        cart.delete()

    def test_fulfilled_cart_convert_loan_to_disbursement_staff_quantity_equal_max_value_with_returned(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        item = Item.objects.create(name="test_item128937", quantity=10)
        cart = RequestCart.objects.create(owner=self.receiver, status="fulfilled", reason="lit")
        loan = Loan.objects.create(item=item, cart=cart, quantity=10, returned_quantity=5)
        data = {'current_type': 'loan', 'pk': loan.id, 'quantity': loan.quantity - loan.returned_quantity}
        url = reverse('convert-request-type')
        response = self.client.post(path=url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response_json = json.loads(str(response.content, 'utf-8'))
        disbursement = Disbursement.objects.get(pk=response_json['id'])
        self.assertEqual(loan.item.name, disbursement.item.name)
        self.assertEqual(data['quantity'], disbursement.quantity)
        self.assertEqual(loan.cart.owner.username, disbursement.cart.owner.username)
        self.assertEqual(Loan.objects.get(pk=loan.id).returned_quantity, Loan.objects.get(pk=loan.id).quantity)
        self.assertTrue(Loan.objects.get(pk=loan.id).returned_timestamp is not None)
        cart.delete()

    def test_outstanding_cart_convert_disbursement_to_loan_staff_quantity_equal_max_value(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        item = Item.objects.create(name="test_item128937", quantity=10)
        cart = RequestCart.objects.create(owner=self.receiver, status="outstanding", reason="lit")
        disbursement = Disbursement.objects.create(item=item, cart=cart, quantity=10)
        data = {'current_type': 'disbursement', 'pk': disbursement.id, 'quantity': disbursement.quantity}
        url = reverse('convert-request-type')
        response = self.client.post(path=url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response_json = json.loads(str(response.content, 'utf-8'))
        loan = Loan.objects.get(pk=response_json['id'])
        self.assertEqual(loan.item.name, disbursement.item.name)
        self.assertEqual(loan.quantity, disbursement.quantity)
        self.assertEqual(loan.cart.owner.username, disbursement.cart.owner.username)
        self.assertFalse(Disbursement.objects.filter(pk=disbursement.id).exists())
        cart.delete()

    def test_fulfilled_cart_convert_loan_to_disbursement_staff_quantity_less_max_value_no_returned(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        item = Item.objects.create(name="test_item128937", quantity=10)
        cart = RequestCart.objects.create(owner=self.receiver, status="fulfilled", reason="lit")
        loan = Loan.objects.create(item=item, cart=cart, quantity=10)
        data = {'current_type': 'loan', 'pk': loan.id, 'quantity': loan.quantity - loan.returned_quantity - 2}
        url = reverse('convert-request-type')
        response = self.client.post(path=url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response_json = json.loads(str(response.content, 'utf-8'))
        disbursement = Disbursement.objects.get(pk=response_json['id'])
        self.assertEqual(loan.item.name, disbursement.item.name)
        self.assertEqual(data['quantity'], disbursement.quantity)
        self.assertEqual(loan.cart.owner.username, disbursement.cart.owner.username)
        self.assertEqual(Loan.objects.get(pk=loan.id).quantity, loan.quantity - data['quantity'])
        self.assertTrue(Loan.objects.get(pk=loan.id).returned_timestamp is None)
        cart.delete()

    def test_fulfilled_cart_convert_loan_to_disbursement_staff_quantity_less_max_value_with_returned(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        item = Item.objects.create(name="test_item128937", quantity=10)
        cart = RequestCart.objects.create(owner=self.receiver, status="fulfilled", reason="lit")
        loan = Loan.objects.create(item=item, cart=cart, quantity=10, returned_quantity=5)
        data = {'current_type': 'loan', 'pk': loan.id, 'quantity': loan.quantity - loan.returned_quantity - 2}
        url = reverse('convert-request-type')
        response = self.client.post(path=url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response_json = json.loads(str(response.content, 'utf-8'))
        disbursement = Disbursement.objects.get(pk=response_json['id'])
        self.assertEqual(loan.item.name, disbursement.item.name)
        self.assertEqual(data['quantity'], disbursement.quantity)
        self.assertEqual(loan.cart.owner.username, disbursement.cart.owner.username)
        self.assertEqual(Loan.objects.get(pk=loan.id).quantity, loan.quantity - data['quantity'])
        self.assertTrue(Loan.objects.get(pk=loan.id).returned_timestamp is None)
        cart.delete()

    def test_outstanding_cart_convert_disbursement_to_loan_staff_quantity_less_max_value(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        item = Item.objects.create(name="test_item128937", quantity=10)
        cart = RequestCart.objects.create(owner=self.receiver, status="outstanding", reason="lit")
        disbursement = Disbursement.objects.create(item=item, cart=cart, quantity=10)
        data = {'current_type': 'disbursement', 'pk': disbursement.id, 'quantity': disbursement.quantity - 2}
        url = reverse('convert-request-type')
        response = self.client.post(path=url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response_json = json.loads(str(response.content, 'utf-8'))
        loan = Loan.objects.get(pk=response_json['id'])
        self.assertEqual(loan.item.name, disbursement.item.name)
        self.assertEqual(data['quantity'], loan.quantity)
        self.assertEqual(loan.cart.owner.username, disbursement.cart.owner.username)
        self.assertEqual(loan.quantity, data['quantity'])
        self.assertEqual(Disbursement.objects.get(pk=disbursement.id).quantity,
                         disbursement.quantity - data['quantity'])
        cart.delete()

    def test_outstanding_cart_convert_disbursement_to_loan_staff_quantity_greater_max_value_fail(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        item = Item.objects.create(name="test_item128937", quantity=10)
        cart = RequestCart.objects.create(owner=self.receiver, status="outstanding", reason="lit")
        disbursement = Disbursement.objects.create(item=item, cart=cart, quantity=10)
        data = {'current_type': 'disbursement', 'pk': disbursement.id, 'quantity': disbursement.quantity + 2}
        url = reverse('convert-request-type')
        response = self.client.post(path=url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(str(response.content, 'utf-8'))['detail'],
                         "Quantity requested, {quantity} does not validate with maximum quantity, {max_quantity}"
                         .format(quantity=data['quantity'], max_quantity=disbursement.quantity))
        cart.delete()

    def test_fulfilled_cart_convert_loan_to_disbursement_staff_quantity_greater_max_value_fail_with_returned(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        item = Item.objects.create(name="test_item128937", quantity=10)
        cart = RequestCart.objects.create(owner=self.receiver, status="fulfilled", reason="lit")
        loan = Loan.objects.create(item=item, cart=cart, quantity=10, returned_quantity=5)
        data = {'current_type': 'loan', 'pk': loan.id, 'quantity': loan.quantity - loan.returned_quantity + 1}
        url = reverse('convert-request-type')
        response = self.client.post(path=url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(str(response.content, 'utf-8'))['detail'],
                         "Quantity requested, {quantity} does not validate with maximum quantity, {max_quantity}"
                         .format(quantity=data['quantity'], max_quantity=loan.quantity-loan.returned_quantity))
        cart.delete()

    def test_cancelled_cart_and_converting_to_loan_fail(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        item = Item.objects.create(name="test_item", quantity=10)
        cart = RequestCart.objects.create(owner=self.receiver, status="cancelled", reason="lit")
        loan = Loan.objects.create(item=item, cart=cart, quantity=10, loaned_timestamp=datetime.now())
        data = {'current_type': 'loan', 'pk': loan.id}
        url = reverse('convert-request-type')
        response = self.client.post(path=url, data=data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(json.loads(str(response.content, 'utf-8'))['detail'],
                         "Cannot change request_type due to cart_status {status}".format(status=cart.status))
        cart.delete()

    def test_denied_cart_and_converting_to_loan_fail(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        item = Item.objects.create(name="test_item", quantity=10)
        cart = RequestCart.objects.create(owner=self.receiver, status="denied", reason="lit", staff=self.admin,
                                          staff_timestamp=datetime.now())
        loan = Loan.objects.create(item=item, cart=cart, quantity=10, loaned_timestamp=datetime.now())
        data = {'current_type': 'loan', 'pk': loan.id}
        url = reverse('convert-request-type')
        response = self.client.post(path=url, data=data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(json.loads(str(response.content, 'utf-8'))['detail'],
                         "Cannot change request_type due to cart_status {status}".format(status=cart.status))
        cart.delete()
