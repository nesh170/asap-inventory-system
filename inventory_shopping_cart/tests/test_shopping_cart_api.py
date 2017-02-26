import json
from datetime import timedelta, timezone, datetime

from django.contrib.auth.models import User
from django.urls import reverse
from oauth2_provider.admin import Application
from oauth2_provider.models import AccessToken
from oauth2_provider.settings import oauth2_settings
from rest_framework import status
from rest_framework.test import APITestCase

from inventory_transaction_logger.action_enum import ActionEnum
from inventory_transaction_logger.models import Action
from inventory_shopping_cart.models import ShoppingCart
from inventory_shopping_cart_request.models import RequestTable
from items.models import Item
from django.core.exceptions import ObjectDoesNotExist

# username and password to create superuser for testing
USERNAME = 'test'
PASSWORD = 'testPassword'
'''
    This Function tests is the JSON representation of a request (either returned from a GET request or posted using a
    POST request) is equivalent to the information that is stored in the database. In the case of a GET request, the JSON
    represents the data that is returned from the request to retrieve information about a request from the database. This
    function compares those things. In the case of a POST request, JSON is used to post information to the server, and
    that information is then stored/updated in the database. These two things are being compared by this function (the
    new information in the database and the JSON representation that was sent using a POST request).
'''


#this function tests if the JSON representation of a request (either returned from a get request
def equal_shopping_cart(test_client, shopping_cart_json, shopping_cart_id):
    shopping_cart = ShoppingCart.objects.get(pk=shopping_cart_id)
    test_client.assertEqual(shopping_cart_json.get('owner'), shopping_cart.owner.id) if type(shopping_cart_json.get('owner')) is int \
        else test_client.assertEqual(shopping_cart_json.get('owner').get('id'), shopping_cart.owner.id)
    test_client.assertEqual(shopping_cart_json.get('status'), shopping_cart.status)
    test_client.assertEqual(shopping_cart_json.get('reason'), shopping_cart.reason)
    test_client.assertEqual(shopping_cart_json.get('admin_comment'), shopping_cart.admin_comment)
    if shopping_cart_json.get('admin') is not None:
        test_client.assertEqual(shopping_cart_json.get('admin'), shopping_cart.admin.id) if type(shopping_cart_json.get('admin')) is int \
            else test_client.assertEqual(shopping_cart_json.get('admin').get('id'), shopping_cart.admin.id)
    requestsJSON = shopping_cart_json.get('requests')
    requestsDatabase = shopping_cart.requests.all()
    for x in range(0, len(requestsDatabase)):
        requestDB = requestsDatabase[x]
        requestJSON = requestsJSON[x]
        test_client.assertEqual(requestJSON.get('id'), requestDB.id)
        test_client.assertEqual(requestJSON.get('quantity_requested'), requestDB.quantity_requested)
        test_client.assertEqual(requestJSON.get('item').get('id'), requestDB.item.id)
        test_client.assertEqual(requestJSON.get('item').get('name'), requestDB.item.name)
        test_client.assertEqual(requestJSON.get('item').get('quantity'), requestDB.item.quantity)

def equal_shopping_cart_request(test_client, shopping_cart_request_json, shopping_cart_request_id):
    shopping_cart_request = RequestTable.objects.get(pk=shopping_cart_request_id)
    test_client.assertEqual(shopping_cart_request_json.get('quantity_requested'), shopping_cart_request.quantity_requested)
    test_client.assertEqual(shopping_cart_request_json.get('item').get('id'), shopping_cart_request.item.id)
    test_client.assertEqual(shopping_cart_request_json.get('item').get('quantity'), shopping_cart_request.item.quantity)
    test_client.assertEqual(shopping_cart_request_json.get('item').get('name'), shopping_cart_request.item.name)

class GetRequestTestCases(APITestCase):
    fixtures = ['shopping_cart_action.json']

    def setUp(self):
        self.admin = User.objects.create_superuser(USERNAME, 'test@test.com', PASSWORD)
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
        oauth2_settings._DEFAULT_SCOPES = ['read','write','groups']
        item_with_one_tag = Item.objects.create(name="quad 2-input NAND gate", quantity=5, model_number="48979",
                                                description="Jameco")
        item_with_one_tag.tags.create(tag="test")
        shopping_cart = ShoppingCart.objects.create(owner=self.admin, status="active", reason="test shopping cart",
                                                    admin_comment="this is an admin comment", admin=self.admin)
        shopping_cart_request = RequestTable.objects.create(item=item_with_one_tag, quantity_requested=2, shopping_cart=shopping_cart)

    def test_get_shopping_carts(self):
        url = reverse('shopping-cart-list')
        self.client.force_authenticate(user=self.admin, token=self.tok)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # converts response to a string and then to a JSON dictionary, and then gets results attribute of it
        json_request_list = json.loads(str(response.content, 'utf-8'))['results']
        #verifies the number of requests returned by the GET request is the same as the number of requests in the database
        #self.assertEqual(json.loads(str(response.content, 'utf-8'))['count'], Request.objects.count())
        # for each request returned by GET request, all equal_request on each one to verify the JSON representation
        # contains the same information as the information in the database
        [equal_shopping_cart(self, json_request, json_request.get('id')) for json_request in json_request_list]

    def test_get_detailed_shopping_cart(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        for shopping_cart_id in ShoppingCart.objects.values_list('id', flat=True):
            url = reverse('detailed-shopping-cart', kwargs={'pk': str(shopping_cart_id)})
            #make the get request
            response = self.client.get(url)
            #compare the JSON response received from the GET request to what is in database
            equal_shopping_cart(self, json.loads(str(response.content, 'utf-8')), shopping_cart_id)


    #this tests the case where an active shopping cart already exists
    def test_get_active_shopping_cart_already_exists(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        url = reverse('active-cart')
        response = self.client.get(url)
        active_shopping_cart = ShoppingCart.objects.get(status="active")
        equal_shopping_cart(self, json.loads(str(response.content, 'utf-8')), active_shopping_cart.id)

class ActiveCartTestCase(APITestCase):
    fixtures = ['shopping_cart_action.json']

    def setUp(self):
        self.admin = User.objects.create_superuser(USERNAME, 'test@test.com', PASSWORD)
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
        oauth2_settings._DEFAULT_SCOPES = ['read','write','groups']
        item_with_one_tag = Item.objects.create(name="quad 2-input NAND gate", quantity=5, model_number="48979",
                                                description="Jameco")
        item_with_one_tag.tags.create(tag="test")
        shopping_cart = ShoppingCart.objects.create(owner=self.admin, status="outstanding", reason="test shopping cart",
                                                    admin_comment="this is an admin comment", admin=self.admin)
        shopping_cart_request = RequestTable.objects.create(item=item_with_one_tag, quantity_requested=2, shopping_cart=shopping_cart)

    def test_get_active_shopping_cart_not_exists(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        url = reverse('active-cart')
        response = self.client.get(url)
        active_shopping_cart = ShoppingCart.objects.get(status="active")
        equal_shopping_cart(self, json.loads(str(response.content, 'utf-8')), active_shopping_cart.id)

class PostRequestTestCases(APITestCase):
    fixtures = ['shopping_cart_action.json']

    def setUp(self):
        self.admin = User.objects.create_superuser(USERNAME, 'test@test.com', PASSWORD)
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
        oauth2_settings._DEFAULT_SCOPES = ['read','write','groups']

    def test_add_item(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        item_with_one_tag = Item.objects.create(name="oscilloscope", quantity=3, model_number="48979",
                                                description="oscilloscope")
        item_with_one_tag.tags.create(tag="test")
        item_with_zero_tags = Item.objects.create(name="resistor", quantity=5, model_number="456789",
                                                  description="resistor")
        shopping_cart_to_add_to = ShoppingCart.objects.create(owner=self.admin, status="active",
                                                            reason="test shopping cart", admin_comment="this is an admin comment", admin=self.admin)
        shopping_cart_request = RequestTable.objects.create(item=item_with_one_tag, quantity_requested=1, shopping_cart=shopping_cart_to_add_to)
        url = reverse('add-to-cart')
        data = {'item_id': item_with_zero_tags.id, 'quantity_requested': 2}
        response = self.client.post(url, data, format='json')
        updated_shopping_cart = ShoppingCart.objects.get(pk=shopping_cart_to_add_to.id)
        json_response = json.loads(str(response.content, 'utf-8'))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        equal_shopping_cart_request(self, json_response, json_response.get('id'))
        updated_shopping_cart_requests = updated_shopping_cart.requests.all()
        #tests if new item exists in shopping cart
        add_success = False
        if (updated_shopping_cart_requests.filter(item=item_with_zero_tags).exists()):
            add_success = True
        self.assertEqual(add_success, True)

    def test_add_item_fail_already_exists(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        item_with_one_tag = Item.objects.create(name="oscilloscope", quantity=3, model_number="48979",
                                                description="oscilloscope")
        item_with_one_tag.tags.create(tag="test")

        shopping_cart_to_add_to = ShoppingCart.objects.create(owner=self.admin, status="active",
                                                            reason="test shopping cart", admin_comment="this is an admin comment", admin=self.admin)
        shopping_cart_request = RequestTable.objects.create(item=item_with_one_tag, quantity_requested=1, shopping_cart=shopping_cart_to_add_to)
        url = reverse('add-to-cart')
        data = {'item_id': item_with_one_tag.id, 'quantity_requested': 2}
        response = self.client.post(url, data, format='json')
        updated_shopping_cart = ShoppingCart.objects.get(pk=shopping_cart_to_add_to.id)
        updated_requests_cart = updated_shopping_cart.requests.all()
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(updated_requests_cart.count(), 1)

    def test_add_item_fail_quantity_negative(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        item_with_one_tag = Item.objects.create(name="oscilloscope", quantity=3, model_number="48979",
                                                description="oscilloscope")
        item_with_one_tag.tags.create(tag="test")
        item_with_zero_tags = Item.objects.create(name="resistor", quantity=5, model_number="456789",
                                                  description="resistor")
        shopping_cart_to_add_to = ShoppingCart.objects.create(owner=self.admin, status="active",
                                                            reason="test shopping cart", admin_comment="this is an admin comment", admin=self.admin)
        shopping_cart_request = RequestTable.objects.create(item=item_with_one_tag, quantity_requested=1, shopping_cart=shopping_cart_to_add_to)
        url = reverse('add-to-cart')
        data = {'item_id': item_with_zero_tags.id, 'quantity_requested': -2}
        response = self.client.post(url, data, format='json')
        updated_shopping_cart = ShoppingCart.objects.get(pk=shopping_cart_to_add_to.id)
        updated_requests_cart = updated_shopping_cart.requests.all()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        addFail = False
        try:
            updated_requests_cart.get(item=item_with_zero_tags)
        except ObjectDoesNotExist:
            addFail = True
        self.assertEqual(addFail, True)

    def test_add_item_fail_not_active_shopping_cart(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        item_with_one_tag = Item.objects.create(name="oscilloscope", quantity=3, model_number="48979", description="oscilloscope")
        item_with_one_tag.tags.create(tag="test")
        item_with_zero_tags = Item.objects.create(name="resistor", quantity=5, model_number="456789", description="resistor")
        shopping_cart_to_add_to = ShoppingCart.objects.create(owner=self.admin, status="outstanding", reason="test shopping cart",
                                                              admin_comment="this is an admin comment", admin=self.admin)
        shopping_cart_request = RequestTable.objects.create(item=item_with_one_tag, quantity_requested=1, shopping_cart=shopping_cart_to_add_to)
        url = reverse('add-to-cart')
        data = {'item_id': item_with_zero_tags.id, 'quantity_requested': 2}
        response = self.client.post(url, data, format='json')
        updated_shopping_cart = ShoppingCart.objects.get(pk=shopping_cart_to_add_to.id)
        updated_requests_cart = updated_shopping_cart.requests.all()
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        addFail = False
        try:
            updated_requests_cart.get(item=item_with_zero_tags)
        except ObjectDoesNotExist:
            addFail = True
        self.assertEqual(addFail, True)

class DeleteItemTestCases(APITestCase):
    fixtures = ['shopping_cart_action.json']

    def setUp(self):
        self.admin = User.objects.create_superuser(USERNAME, 'test@test.com', PASSWORD)
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
        oauth2_settings._DEFAULT_SCOPES = ['read','write','groups']

    def test_delete_item(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        item_with_one_tag = Item.objects.create(name="oscilloscope", quantity=3, model_number="48979",
                                                description="oscilloscope")
        item_with_one_tag.tags.create(tag="test")
        item_with_zero_tags = Item.objects.create(name="resistor", quantity=5, model_number="456789",
                                                  description="resistor")
        shopping_cart_to_delete_from = ShoppingCart.objects.create(owner=self.admin, status="active",
                                                            reason="test shopping cart", admin_comment="this is an admin comment", admin=self.admin)
        shopping_cart_request = RequestTable.objects.create(item=item_with_one_tag, quantity_requested=1, shopping_cart=shopping_cart_to_delete_from)
        shopping_cart_request_second_item = RequestTable.objects.create(item=item_with_zero_tags, quantity_requested=2, shopping_cart=shopping_cart_to_delete_from)
        url = reverse('delete-from-cart', kwargs={'pk': str(shopping_cart_request_second_item.id)})
        response = self.client.delete(url)
        updated_shopping_cart = ShoppingCart.objects.get(pk=shopping_cart_to_delete_from.id)
        updated_requests_cart = updated_shopping_cart.requests.all()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        delete_success = False
        #request no longer in request table
        try:
            RequestTable.objects.get(pk=shopping_cart_request_second_item.id)
        except ObjectDoesNotExist:
            delete_success = True
        self.assertEqual(delete_success, True)
        #request no longer in the shopping cart
        delete_success_cart = False
        try:
            updated_requests_cart.get(pk=shopping_cart_request_second_item.id)
        except ObjectDoesNotExist:
            delete_success_cart = True
        self.assertEqual(delete_success_cart, True)


    def test_delete_item_fail_not_active_shopping_cart(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        item_with_one_tag = Item.objects.create(name="oscilloscope", quantity=3, model_number="48979",
                                                description="oscilloscope")
        item_with_one_tag.tags.create(tag="test")
        item_with_zero_tags = Item.objects.create(name="resistor", quantity=5, model_number="456789",
                                                  description="resistor")
        shopping_cart_to_delete_from = ShoppingCart.objects.create(owner=self.admin, status="outstanding",
                                                            reason="test shopping cart", admin_comment="this is an admin comment", admin=self.admin)
        shopping_cart_request = RequestTable.objects.create(item=item_with_one_tag, quantity_requested=1, shopping_cart=shopping_cart_to_delete_from)
        shopping_cart_request_second_item = RequestTable.objects.create(item=item_with_zero_tags, quantity_requested=2, shopping_cart=shopping_cart_to_delete_from)
        url = reverse('delete-from-cart', kwargs={'pk': str(shopping_cart_request_second_item.id)})
        response = self.client.delete(url)
        updated_shopping_cart = ShoppingCart.objects.get(pk=shopping_cart_to_delete_from.id)
        updated_requests_cart = updated_shopping_cart.requests.all()
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        delete_fail = False
        if (updated_requests_cart.filter(pk=shopping_cart_request_second_item.id).exists()):
            delete_fail = True
        self.assertEqual(delete_fail, True)


    def test_delete_item_fail_not_exists(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        item_with_one_tag = Item.objects.create(name="oscilloscope", quantity=3, model_number="48979",
                                                description="oscilloscope")
        item_with_one_tag.tags.create(tag="test")
        item_with_zero_tags = Item.objects.create(name="resistor", quantity=5, model_number="456789",
                                                  description="resistor")
        shopping_cart_to_delete_from = ShoppingCart.objects.create(owner=self.admin, status="active",
                                                            reason="test shopping cart", admin_comment="this is an admin comment", admin=self.admin)
        shopping_cart_request = RequestTable.objects.create(item=item_with_one_tag, quantity_requested=1, shopping_cart=shopping_cart_to_delete_from)
        another_shopping_cart = ShoppingCart.objects.create(owner=self.admin, status="outstanding", reason="test shopping cart",
                                                                   admin_comment="this is an admin comment", admin=self.admin)
        shopping_cart_request_second_item = RequestTable.objects.create(item=item_with_zero_tags, quantity_requested=2, shopping_cart=another_shopping_cart)
        #shoppping_cart_request_second_item doesn't exist in active shopping cart
        url = reverse('delete-from-cart', kwargs={'pk': str(shopping_cart_request_second_item.id)})
        response = self.client.delete(url)
        #should still be in another shopping cart
        updated_shopping_cart = ShoppingCart.objects.get(pk=another_shopping_cart.id)
        updated_requests_cart = updated_shopping_cart.requests.all()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        #shopping cart request for second item should still be in another_shopping_cart
        delete_fail = False
        if (updated_requests_cart.filter(pk=shopping_cart_request_second_item.id).exists()):
            delete_fail = True
        self.assertEqual(delete_fail, True)


class PatchRequestTestCases(APITestCase):
    fixtures = ['shopping_cart_action.json']

    def setUp(self):
        self.admin = User.objects.create_superuser(USERNAME, 'test@test.com', PASSWORD)
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
        oauth2_settings._DEFAULT_SCOPES = ['read','write','groups']

    def test_send_cart(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        item_with_one_tag = Item.objects.create(name="oscilloscope", quantity=3, model_number="48979",
                                                description="oscilloscope")
        item_with_one_tag.tags.create(tag="test")
        item_with_zero_tags = Item.objects.create(name="resistor", quantity=5, model_number="456789", description="resistor")
        shopping_cart_to_send = ShoppingCart.objects.create(owner=self.admin, status="active", reason="test shopping cart",
                                                               admin_comment="this is an admin comment", admin=self.admin)
        shopping_cart_request = RequestTable.objects.create(item=item_with_one_tag, quantity_requested=1, shopping_cart=shopping_cart_to_send)
        shopping_cart_request_item_two = RequestTable.objects.create(item=item_with_zero_tags, quantity_requested=2, shopping_cart=shopping_cart_to_send)
        data = {'id': shopping_cart_to_send.id, 'reason': "testing send cart"}
        url = reverse('send-cart', kwargs={'pk': str(shopping_cart_to_send.id)})
        response = self.client.patch(url, data, format='json')
        updated_shopping_cart = ShoppingCart.objects.get(pk=shopping_cart_to_send.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(updated_shopping_cart.status, "outstanding")
        equal_shopping_cart(self, json.loads(str(response.content, 'utf-8')), shopping_cart_to_send.id)

    def test_send_cart_fail_status(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        item_with_one_tag = Item.objects.create(name="oscilloscope", quantity=3, model_number="48979",
                                                description="oscilloscope")
        item_with_one_tag.tags.create(tag="test")
        item_with_zero_tags = Item.objects.create(name="resistor", quantity=5, model_number="456789", description="resistor")
        shopping_cart_to_send = ShoppingCart.objects.create(owner=self.admin, status="outstanding", reason="test shopping cart",
                                                               admin_comment="this is an admin comment", admin=self.admin)
        shopping_cart_request = RequestTable.objects.create(item=item_with_one_tag, quantity_requested=1, shopping_cart=shopping_cart_to_send)
        shopping_cart_request_item_two = RequestTable.objects.create(item=item_with_zero_tags, quantity_requested=2, shopping_cart=shopping_cart_to_send)
        data = {'id': shopping_cart_to_send.id, 'reason': "testing send cart"}
        url = reverse('send-cart', kwargs={'pk': str(shopping_cart_to_send.id)})
        response = self.client.patch(url, data, format='json')
        updated_shopping_cart = ShoppingCart.objects.get(pk=shopping_cart_to_send.id)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(updated_shopping_cart.status, shopping_cart_to_send.status)
        self.assertEqual(updated_shopping_cart.reason, shopping_cart_to_send.reason)


    def test_modify_quantity(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        item_with_one_tag = Item.objects.create(name="oscilloscope", quantity=3, model_number="48979",
                                                description="oscilloscope")
        item_with_one_tag.tags.create(tag="test")
        shopping_cart_to_modify = ShoppingCart.objects.create(owner=self.admin, status="active", reason="test shopping cart",
                                                               admin_comment="this is an admin comment", admin=self.admin)
        shopping_cart_request = RequestTable.objects.create(item=item_with_one_tag, quantity_requested=1, shopping_cart=shopping_cart_to_modify)
        data = {'item_id': item_with_one_tag.id, 'quantity_requested': 2}
        url = reverse('modify-quantity-requested', kwargs={'pk': str(shopping_cart_request.id)})
        response = self.client.patch(url, data, format='json')
        updated_shopping_cart_request = RequestTable.objects.get(pk=shopping_cart_request.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(updated_shopping_cart_request.quantity_requested, data.get('quantity_requested'))

    def test_modify_quantity_fail_status(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        item_with_one_tag = Item.objects.create(name="oscilloscope", quantity=3, model_number="48979",
                                                description="oscilloscope")
        item_with_one_tag.tags.create(tag="test")
        shopping_cart_to_modify = ShoppingCart.objects.create(owner=self.admin, status="outstanding", reason="test shopping cart",
                                                               admin_comment="this is an admin comment", admin=self.admin)
        shopping_cart_request = RequestTable.objects.create(item=item_with_one_tag, quantity_requested=1, shopping_cart=shopping_cart_to_modify)
        data = {'item_id': item_with_one_tag.id, 'quantity_requested': 2}
        url = reverse('modify-quantity-requested', kwargs={'pk': str(shopping_cart_request.id)})
        response = self.client.patch(url, data, format='json')
        updated_shopping_cart_request = RequestTable.objects.get(pk=shopping_cart_request.id)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(updated_shopping_cart_request.quantity_requested, shopping_cart_request.quantity_requested)

    def test_modify_quantity_fail_negative_quantity(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        item_with_one_tag = Item.objects.create(name="oscilloscope", quantity=3, model_number="48979",
                                                description="oscilloscope")
        item_with_one_tag.tags.create(tag="test")
        shopping_cart_to_modify = ShoppingCart.objects.create(owner=self.admin, status="active", reason="test shopping cart",
                                                               admin_comment="this is an admin comment", admin=self.admin)
        shopping_cart_request = RequestTable.objects.create(item=item_with_one_tag, quantity_requested=1, shopping_cart=shopping_cart_to_modify)
        data = {'item_id': item_with_one_tag.id, 'quantity_requested': -5}
        url = reverse('modify-quantity-requested', kwargs={'pk': str(shopping_cart_request.id)})
        response = self.client.patch(url, data, format='json')
        updated_shopping_cart_request = RequestTable.objects.get(pk=shopping_cart_request.id)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(updated_shopping_cart_request.quantity_requested, shopping_cart_request.quantity_requested)

    def test_approve_shopping_cart(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        item_with_one_tag = Item.objects.create(name="oscilloscope", quantity=3, model_number="48979",
                                                description="oscilloscope")
        item_with_one_tag.tags.create(tag="test")
        shopping_cart_to_approve = ShoppingCart.objects.create(owner=self.admin, status="outstanding", reason="test shopping cart",
                                                    admin_comment="this is an admin comment", admin=self.admin)
        shopping_cart_request = RequestTable.objects.create(item=item_with_one_tag, quantity_requested=2, shopping_cart=shopping_cart_to_approve)
        data = {'id': shopping_cart_to_approve.id, 'admin_comment': 'testing approve request'}
        url = reverse('approve-shopping-cart', kwargs={'pk': str(shopping_cart_to_approve.id)})
        response = self.client.patch(url, data, format='json')
        updated_shopping_cart = ShoppingCart.objects.get(pk=shopping_cart_to_approve.id)
        updated_item = Item.objects.get(pk=item_with_one_tag.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(updated_shopping_cart.status, "approved")
        self.assertEqual(updated_item.quantity, item_with_one_tag.quantity - shopping_cart_request.quantity_requested)
        self.assertEqual(updated_shopping_cart.admin_comment, "testing approve request")

    def test_approve_shopping_cart_fail_quantity(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        item_with_one_tag = Item.objects.create(name="oscilloscope", quantity=3, model_number="48979",
                                                description="oscilloscope")
        item_with_one_tag.tags.create(tag="test")
        shopping_cart_to_approve = ShoppingCart.objects.create(owner=self.admin, status="outstanding", reason="test shopping cart",
                                                               admin_comment="this is an admin comment", admin=self.admin)
        shopping_cart_request = RequestTable.objects.create(item=item_with_one_tag, quantity_requested=4, shopping_cart=shopping_cart_to_approve)
        data = {'id': shopping_cart_to_approve.id, 'admin_comment': 'testing approve request'}
        url = reverse('approve-shopping-cart', kwargs={'pk': str(shopping_cart_to_approve.id)})
        response = self.client.patch(url, data, format='json')
        updated_item = Item.objects.get(pk=item_with_one_tag.id)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(item_with_one_tag.quantity, updated_item.quantity)

    def test_approve_shopping_cart_fail_status(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        item_with_one_tag = Item.objects.create(name="oscilloscope", quantity=3, model_number="48979",
                                                description="oscilloscope")
        item_with_one_tag.tags.create(tag="test")
        shopping_cart_to_approve = ShoppingCart.objects.create(owner=self.admin, status="denied", reason="test shopping cart",
                                                               admin_comment="this is an admin comment", admin=self.admin)
        shopping_cart_request = RequestTable.objects.create(item=item_with_one_tag, quantity_requested=4, shopping_cart=shopping_cart_to_approve)
        data = {'id': shopping_cart_to_approve.id, 'admin_comment': 'testing approve request'}
        url = reverse('approve-shopping-cart', kwargs={'pk': str(shopping_cart_to_approve.id)})
        response = self.client.patch(url, data, format='json')
        updated_item = Item.objects.get(pk=item_with_one_tag.id)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(item_with_one_tag.quantity, updated_item.quantity)

    def test_deny_shopping_cart(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        item_with_one_tag = Item.objects.create(name="oscilloscope", quantity=3, model_number="48979",
                                                description="oscilloscope")
        item_with_one_tag.tags.create(tag="test")
        shopping_cart_to_deny = ShoppingCart.objects.create(owner=self.admin, status="outstanding", reason="test shopping cart",
                                                               admin_comment="this is an admin comment", admin=self.admin)
        shopping_cart_request = RequestTable.objects.create(item=item_with_one_tag, quantity_requested=4,
                                                            shopping_cart=shopping_cart_to_deny)
        data = {'id': shopping_cart_to_deny.id, 'admin_comment': 'testing deny request'}
        url = reverse('deny-shopping-cart', kwargs={'pk': str(shopping_cart_to_deny.id)})
        response = self.client.patch(url, data, format='json')
        updated_shopping_cart = ShoppingCart.objects.get(pk=shopping_cart_to_deny.id)
        updated_item = Item.objects.get(pk=item_with_one_tag.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(updated_shopping_cart.status, "denied")
        self.assertEqual(updated_item.quantity, item_with_one_tag.quantity)
        self.assertEqual(updated_shopping_cart.admin_comment, "testing deny request")

    def test_deny_shopping_cart_fail(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        item_with_one_tag = Item.objects.create(name="oscilloscope", quantity=3, model_number="48979",
                                                description="oscilloscope")
        item_with_one_tag.tags.create(tag="test")
        shopping_cart_to_deny = ShoppingCart.objects.create(owner=self.admin, status="cancelled", reason="test shopping cart",
                                                               admin_comment="this is an admin comment", admin=self.admin)
        shopping_cart_request = RequestTable.objects.create(item=item_with_one_tag, quantity_requested=2,
                                                            shopping_cart=shopping_cart_to_deny)
        data = {'id': shopping_cart_to_deny.id, 'admin_comment': 'testing deny request'}
        url = reverse('deny-shopping-cart', kwargs={'pk': str(shopping_cart_to_deny.id)})
        response = self.client.patch(url, data, format='json')
        updated_shopping_cart = ShoppingCart.objects.get(pk=shopping_cart_to_deny.id)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(shopping_cart_to_deny.admin_comment, updated_shopping_cart.admin_comment)
        self.assertEqual(shopping_cart_to_deny.status, updated_shopping_cart.status)

    def test_cancel_shopping_cart_fail(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        item_with_one_tag = Item.objects.create(name="oscilloscope", quantity=3, model_number="48979",
                                                description="oscilloscope")
        item_with_one_tag.tags.create(tag="test")
        shopping_cart_to_cancel = ShoppingCart.objects.create(owner=self.admin, status="approved", reason="test shopping cart",
                                                               admin_comment="this is an admin comment", admin=self.admin)
        shopping_cart_request = RequestTable.objects.create(item=item_with_one_tag, quantity_requested=2,
                                                            shopping_cart=shopping_cart_to_cancel)
        data = {'id': shopping_cart_to_cancel.id, 'reason': 'testing cancellation of request, should not work'}
        url = reverse('cancel-shopping-cart', kwargs={'pk': str(shopping_cart_to_cancel.id)})
        response = self.client.patch(url, data, format='json')
        updated_shopping_cart = ShoppingCart.objects.get(pk=shopping_cart_to_cancel.id)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(shopping_cart_to_cancel.reason, updated_shopping_cart.reason)
        self.assertEqual(shopping_cart_to_cancel.status, updated_shopping_cart.status)


    def test_cancel_shopping_cart(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        item_with_one_tag = Item.objects.create(name="oscilloscope", quantity=3, model_number="48979",
                                                description="oscilloscope")
        item_with_one_tag.tags.create(tag="test")
        shopping_cart_to_cancel = ShoppingCart.objects.create(owner=self.admin, status="outstanding", reason="test shopping cart",
                                                              admin_comment="this is an admin comment", admin=self.admin)
        shopping_cart_request = RequestTable.objects.create(item=item_with_one_tag, quantity_requested=2, shopping_cart=shopping_cart_to_cancel)
        data = {'id': shopping_cart_to_cancel.id, 'reason': 'testing cancellation of request, should not work'}
        url = reverse('cancel-shopping-cart', kwargs={'pk': str(shopping_cart_to_cancel.id)})
        response = self.client.patch(url, data, format='json')
        updated_shopping_cart = ShoppingCart.objects.get(pk=shopping_cart_to_cancel.id)
        updated_item = Item.objects.get(pk=item_with_one_tag.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(item_with_one_tag.quantity, updated_item.quantity)
        self.assertEqual(updated_shopping_cart.status, "cancelled")