import json
from datetime import timezone, datetime, timedelta

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from oauth2_provider.admin import Application
from oauth2_provider.models import AccessToken
from oauth2_provider.settings import oauth2_settings
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from inventory_disbursements.models import Disbursement, Cart
from items.models import Item

USERNAME = 'test'
PASSWORD = 'testPassword'

TEST_USERNAME = 'ankit'
TEST_PASSWORD = 'lol'


def equal_disbursement(client, cart_id, disbursement_id, data):
    disbursement_item = Disbursement.objects.get(pk=disbursement_id)
    client.assertEqual(cart_id, disbursement_item.cart.id)
    client.assertEqual(disbursement_item.quantity, data.get("quantity"))
    client.assertEqual(disbursement_item.item.id, data.get("item_id"))


def equal_cart(client, cart_id, data):
    cart = Cart.objects.get(pk=cart_id)
    client.assertEqual(cart.disburser.id, data.get('disburser').get('id'))
    if cart.receiver is not None:
        client.assertEqual(cart.receiver.id, data.get('receiver_id'))
    [equal_disbursement(client=client, cart_id=disbursement.get('cart_id'), disbursement_id=disbursement.get('id'),
                        data=disbursement) for disbursement in data.get('disbursements')]


class DisbursementAPITest(APITestCase):
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
        oauth2_settings._DEFAULT_SCOPES = ['read', 'write', 'groups']
        self.item = Item.objects.create(name='item_1', quantity=50)
        self.cart = Cart.objects.create(disburser=self.admin)
        self.disbursement = Disbursement.objects.create(cart=self.cart, item=self.item, quantity=3)

    def test_get_disbursements_cart(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        url = reverse('cart-list')
        response = self.client.get(path=url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json_response = json.loads(str(response.content, 'utf-8'))
        self.assertEqual(json_response['count'], Cart.objects.count())
        json_disbursement_list = json_response['results']
        [equal_cart(self, cart.get('id'), cart) for cart in json_disbursement_list]

    def test_get_existing_active_cart(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        url = reverse('active-disbursement-cart')
        response = self.client.get(path=url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json_response = json.loads(str(response.content, 'utf-8'))
        active_cart_id = Cart.objects.get(receiver=None, disburser=self.admin).id
        self.assertEqual(active_cart_id, json_response.get('id'))
        equal_cart(self, active_cart_id, json_response)

    def test_get_new_active_cart(self):
        self.cart.receiver = self.receiver
        self.cart.save()
        self.client.force_authenticate(user=self.admin, token=self.tok)
        url = reverse('active-disbursement-cart')
        response = self.client.get(path=url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json_response = json.loads(str(response.content, 'utf-8'))
        self.assertNotEqual(self.cart.id, json_response.get('id'))
        active_cart_id = Cart.objects.get(receiver=None, disburser=self.admin).id
        self.assertEqual(active_cart_id, json_response.get('id'))
        self.cart.receiver = None
        self.cart.save()

    def test_cart_submission_non_active_cart(self):
        self.cart.receiver = self.receiver
        self.cart.save()
        self.client.force_authenticate(user=self.admin, token=self.tok)
        data = {'receiver_id': self.receiver.id, 'comment': 'lit'}
        url = reverse(viewname='cart-submission', kwargs={'pk': self.cart.id})
        response = self.client.patch(path=url, data=data)
        self.assertEqual(json.loads(str(response.content, 'utf-8'))['detail'], "This cart has been disbursed")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.cart.receiver = None
        self.cart.save()

    def test_cart_submission_invalid_user(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        data = {'receiver_id': 5123, 'comment': 'lit'}
        url = reverse(viewname='cart-submission', kwargs={'pk': self.cart.id})
        response = self.client.patch(path=url, data=data)
        self.assertEqual(json.loads(str(response.content, 'utf-8'))['detail'], "User is not found in database")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_cart_submission_no_receiver_id(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        data = {'comment': 'lit'}
        url = reverse(viewname='cart-submission', kwargs={'pk': self.cart.id})
        response = self.client.patch(path=url, data=data)
        self.assertEqual(json.loads(str(response.content, 'utf-8'))['detail'],
                         "receiver_id is required to submit a cart")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cart_submission_item_quantity_not_satisfied(self):
        item = Item.objects.create(name="ankit", quantity=50)
        disbursement = Disbursement.objects.create(cart=self.cart, item=item, quantity=51)
        self.client.force_authenticate(user=self.admin, token=self.tok)
        data = {'receiver_id': self.receiver.id, 'comment': 'lit'}
        url = reverse(viewname='cart-submission', kwargs={'pk': self.cart.id})
        response = self.client.patch(path=url, data=data)
        self.assertEqual(json.loads(str(response.content, 'utf-8'))['detail'],
                         'Item ankit has quantity 50 but needs to disburse 51')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        disbursement.delete()

    def test_cart_submission_successful(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        data = {'receiver_id': self.receiver.id, 'comment': 'lit'}
        url = reverse(viewname='cart-submission', kwargs={'pk': self.cart.id})
        response = self.client.patch(path=url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        submitted_cart = Cart.objects.get(pk=json.loads(str(response.content, 'utf-8'))['id'])
        self.assertEqual(submitted_cart.id, self.cart.id)
        self.assertEqual(submitted_cart.receiver.id, data.get('receiver_id'))
        self.assertEqual(submitted_cart.comment, data.get('comment'))
        updated_item = Item.objects.get(pk=self.item.id)
        self.assertEqual(updated_item.quantity, self.item.quantity - self.disbursement.quantity)
        self.cart.receiver = None
        self.cart.comment = None
        self.cart.save()

    def test_disbursement_deletion_nonactive_cart(self):
        self.cart.receiver = self.receiver
        self.cart.save()
        self.client.force_authenticate(user=self.admin, token=self.tok)
        url = reverse(viewname='disbursement-deletion', kwargs={'pk': self.disbursement.id})
        response = self.client.delete(path=url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(json.loads(str(response.content, 'utf-8'))['detail'], "You can only modify an active Disbursement Cart")
        self.cart.receiver = None
        self.cart.save()

    def test_disbursement_deletion_successful(self):
        item = Item.objects.create(name="litItem", quantity=10)
        disbursement = Disbursement.objects.create(cart=self.cart, item=item, quantity=4)
        self.client.force_authenticate(user=self.admin, token=self.tok)
        url = reverse(viewname='disbursement-deletion', kwargs={'pk': disbursement.id})
        response = self.client.delete(path=url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        success_delete = False
        try:
            Disbursement.objects.get(pk=disbursement.id)
        except ObjectDoesNotExist:
            success_delete = True
        self.assertEqual(success_delete, True)

    def test_disbursement_creation_item_not_found(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        url = reverse('disbursement-creation')
        data = {'item_id': 14312, 'cart_id':self.cart.id, 'quantity': 2}
        response = self.client.post(path=url, data=data)
        self.assertEqual(json.loads(str(response.content, 'utf-8'))['detail'], "Item is not found in database")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_disbursement_creation_cart_not_found(self):
        item = Item.objects.create(name='random_name_here', quantity=10)
        self.client.force_authenticate(user=self.admin, token=self.tok)
        url = reverse('disbursement-creation')
        data = {'item_id': item.id, 'cart_id': 14312, 'quantity': 2}
        response = self.client.post(path=url, data=data)
        self.assertEqual(json.loads(str(response.content, 'utf-8'))['detail'], "Cart is not found in database")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_disbursement_creation_cart_not_active(self):
        item = Item.objects.create(name='random_name_fire_storm', quantity=123)
        self.cart.receiver = self.receiver
        self.cart.save()
        self.client.force_authenticate(user=self.admin, token=self.tok)
        url = reverse('disbursement-creation')
        data = {'item_id': item.id, 'cart_id': self.cart.id, 'quantity': 2}
        response = self.client.post(path=url, data=data)
        self.assertEqual(json.loads(str(response.content, 'utf-8'))['detail'], "The cart needs to be active")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.cart.receiver = None
        self.cart.save()

    def test_disbursement_creation_item_exists_in_cart(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        url = reverse('disbursement-creation')
        data = {'item_id': self.item.id, 'cart_id': self.cart.id, 'quantity': 1}
        response = self.client.post(path=url, data=data)
        self.assertEqual(json.loads(str(response.content, 'utf-8'))['detail'], "Item is already in cart")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_disbursement_creation_quantity_exceeds_item_quantity(self):
        item = Item.objects.create(name= 'Test Item Work', quantity=100)
        self.client.force_authenticate(user=self.admin, token=self.tok)
        url = reverse('disbursement-creation')
        data = {'item_id': item.id, 'cart_id': self.cart.id, 'quantity': 101}
        response = self.client.post(path=url, data=data)
        self.assertEqual(json.loads(str(response.content, 'utf-8'))['detail'],
                         "Quantity to be disbursed is more than item value")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_disbursement_creation_success(self):
        item = Item.objects.create(name= 'success', quantity=100)
        self.client.force_authenticate(user=self.admin, token=self.tok)
        url = reverse('disbursement-creation')
        data = {'item_id': item.id, 'cart_id': self.cart.id, 'quantity': 30}
        response = self.client.post(path=url, data=data)
        json_response = json.loads(str(response.content, 'utf-8'))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        equal_disbursement(client=self, cart_id=data.get('cart_id'), disbursement_id=json_response.get('id'),
                           data=json_response)





















