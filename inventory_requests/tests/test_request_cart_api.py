import json
from datetime import timedelta, timezone, datetime

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from oauth2_provider.admin import Application
from oauth2_provider.models import AccessToken
from oauth2_provider.settings import oauth2_settings
from rest_framework import status
from rest_framework.test import APITestCase

from inventory_requests.models import RequestCart, Disbursement, Loan
from items.models import Item

# username and password to create superuser for testing
USERNAME = 'test'
PASSWORD = 'testPassword'
TEST_USERNAME = 'ankit'
TEST_PASSWORD = 'lol'
'''
    This Function tests is the JSON representation of a request (either returned from a GET request or posted using a
    POST request) is equivalent to the information that is stored in the database. In the case of a GET request, the JSON
    represents the data that is returned from the request to retrieve information about a request from the database. This
    function compares those things. In the case of a POST request, JSON is used to post information to the server, and
    that information is then stored/updated in the database. These two things are being compared by this function (the
    new information in the database and the JSON representation that was sent using a POST request).
'''


# this function tests if the JSON representation of a request (either returned from a get request
def equal_request_cart(test_client, request_cart_json, request_cart_id):
    request_cart = RequestCart.objects.get(pk=request_cart_id)
    if request_cart_json.get('owner') is not  None:
        test_client.assertEqual(request_cart_json.get('owner'), request_cart.owner.username) \
            if type(request_cart_json.get('owner')) is int else \
            test_client.assertEqual(request_cart_json.get('owner'), request_cart.owner.username)
    test_client.assertEqual(request_cart_json.get('status'), request_cart.status)
    test_client.assertEqual(request_cart_json.get('reason'), request_cart.reason)
    test_client.assertEqual(request_cart_json.get('staff_comment'), request_cart.staff_comment)
    if request_cart_json.get('staff') is not None:
        test_client.assertEqual(request_cart_json.get('staff'), request_cart.staff.username) \
            if type(request_cart_json.get('staff')) is int else \
            test_client.assertEqual(request_cart_json.get('staff'), request_cart.staff.username)
    requests_json = request_cart_json.get('cart_disbursements')
    test_client.assertEqual(len(requests_json), Disbursement.objects.filter(cart=request_cart).count())
    [equal_disbursement(test_client, request_json, request_json.get('id')) for request_json in requests_json]


def equal_disbursement(test_client, disbursement_json, disbursement_id):
    disbursement = Disbursement.objects.get(pk=disbursement_id)
    test_client.assertEqual(disbursement_json.get('quantity'), disbursement.quantity)
    test_client.assertEqual(disbursement_json.get('item').get('id'), disbursement.item.id)
    test_client.assertEqual(disbursement_json.get('item').get('quantity'), disbursement.item.quantity)
    test_client.assertEqual(disbursement_json.get('item').get('name'), disbursement.item.name)


class GetRequestTestCases(APITestCase):
    fixtures = ['requests_action.json']

    def setUp(self):
        self.admin = User.objects.create_superuser(USERNAME, '', PASSWORD)
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
        request_cart = RequestCart.objects.create(owner=self.admin, status="active", reason="test shopping cart",
                                                  staff_comment="this is an admin comment", staff=self.admin)
        Disbursement.objects.create(item=item_with_one_tag, quantity=2, cart=request_cart)

    def test_get_all_requests(self):
        url = reverse('request-cart-list')
        self.client.force_authenticate(user=self.admin, token=self.tok)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # converts response to a string and then to a JSON dictionary, and then gets results attribute of it
        json_request_list = json.loads(str(response.content, 'utf-8'))['results']
        # verifies the number of requests returned by the GET request
        # is the same as the number of requests in the database
        # self.assertEqual(json.loads(str(response.content, 'utf-8'))['count'], Request.objects.count())
        # for each request returned by GET request, all equal_request on each one to verify the JSON representation
        # contains the same information as the information in the database
        [equal_request_cart(self, json_request, json_request.get('id')) for json_request in json_request_list]

    def test_get_detailed_request(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        for request_cart_id in RequestCart.objects.values_list('id', flat=True):
            url = reverse('detailed-request-cart', kwargs={'pk': str(request_cart_id)})
            # make the get request
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            # compare the JSON response received from the GET request to what is in database
            equal_request_cart(self, json.loads(str(response.content, 'utf-8')), request_cart_id)

    # this tests the case where an active request already exists
    def test_get_active_request_already_exists(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        url = reverse('active-cart')
        response = self.client.get(url)
        active_request = RequestCart.objects.get(status="active")
        equal_request_cart(self, json.loads(str(response.content, 'utf-8')), active_request.id)


class ActiveCartTestCase(APITestCase):
    fixtures = ['requests_action.json']

    def setUp(self):
        self.admin = User.objects.create_superuser(USERNAME, '', PASSWORD)
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
        item_with_one_tag = Item.objects.create(name="quad 2-input NAND gate", quantity=5, model_number="48979",
                                                description="Jameco")
        item_with_one_tag.tags.create(tag="test")
        request_cart = RequestCart.objects.create(owner=self.admin, status="outstanding", reason="test shopping cart",
                                                  staff_comment="this is an admin comment", staff=self.admin)
        Disbursement.objects.create(item=item_with_one_tag, quantity=2, cart=request_cart)

    def test_get_active_request_not_exists(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        url = reverse('active-cart')
        response = self.client.get(url)
        active_request = RequestCart.objects.get(status="active")
        equal_request_cart(self, json.loads(str(response.content, 'utf-8')), active_request.id)


class PostRequestTestCases(APITestCase):
    fixtures = ['requests_action.json']

    def setUp(self):
        self.admin = User.objects.create_superuser(USERNAME, '', PASSWORD)
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
        request_to_add_to = RequestCart.objects.create(owner=self.admin, status="active",
                                                       reason="test shopping cart",
                                                       staff_comment="this is an admin comment", staff=self.admin)
        Disbursement.objects.create(item=item_with_one_tag, quantity=1, cart=request_to_add_to)
        url = reverse('add-to-cart')
        data = {'item_id': item_with_zero_tags.id, 'quantity': 2}
        response = self.client.post(url, data, format='json')
        updated_request_cart = RequestCart.objects.get(pk=request_to_add_to.id)
        json_response = json.loads(str(response.content, 'utf-8'))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        equal_disbursement(self, json_response, json_response.get('id'))
        updated_disbursement = updated_request_cart.cart_disbursements.all()
        # tests if new item exists in shopping cart
        add_success = False
        if updated_disbursement.filter(item=item_with_zero_tags).exists():
            add_success = True
        self.assertEqual(add_success, True)

    def test_add_item_fail_already_exists(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        item_with_one_tag = Item.objects.create(name="oscilloscope", quantity=3, model_number="48979",
                                                description="oscilloscope")
        item_with_one_tag.tags.create(tag="test")

        request_cart_to_add_to = RequestCart.objects.create(owner=self.admin, status="active",
                                                            reason="test shopping cart",
                                                            staff_comment="this is an admin comment", staff=self.admin)
        Disbursement.objects.create(item=item_with_one_tag, quantity=1, cart=request_cart_to_add_to)
        url = reverse('add-to-cart')
        data = {'item_id': item_with_one_tag.id, 'quantity': 2}
        response = self.client.post(url, data, format='json')
        updated_disbursements = RequestCart.objects.get(pk=request_cart_to_add_to.id).cart_disbursements.all()
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(updated_disbursements.count(), 1)

    def test_add_item_fail_quantity_negative(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        item_with_one_tag = Item.objects.create(name="oscilloscope", quantity=3, model_number="48979",
                                                description="oscilloscope")
        item_with_one_tag.tags.create(tag="test")
        item_with_zero_tags = Item.objects.create(name="resistor", quantity=5, model_number="456789",
                                                  description="resistor")
        request_to_add_to = RequestCart.objects.create(owner=self.admin, status="active", reason="test shopping cart",
                                                       staff_comment="this is an admin comment", staff=self.admin)
        Disbursement.objects.create(item=item_with_one_tag, quantity=1, cart=request_to_add_to)
        url = reverse('add-to-cart')
        data = {'item_id': item_with_zero_tags.id, 'quantity': -2}
        response = self.client.post(url, data, format='json')
        updated_disbursements = RequestCart.objects.get(pk=request_to_add_to.id).cart_disbursements.all()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        add_fail = False
        try:
            updated_disbursements.get(item=item_with_zero_tags)
        except ObjectDoesNotExist:
            add_fail = True
        self.assertEqual(add_fail, True)

    def test_add_item_fail_not_active_shopping_cart(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        item_with_one_tag = Item.objects.create(name="oscilloscope", quantity=3, model_number="48979",
                                                description="oscilloscope")
        item_with_one_tag.tags.create(tag="test")
        item_with_zero_tags = Item.objects.create(name="resistor", quantity=5, model_number="456789",
                                                  description="resistor")
        request_to_add_to = RequestCart.objects.create(owner=self.admin, status="outstanding", reason="test cart",
                                                       staff_comment="this is an admin comment", staff=self.admin)
        Disbursement.objects.create(item=item_with_one_tag, quantity=1, cart=request_to_add_to)
        url = reverse('add-to-cart')
        data = {'item_id': item_with_zero_tags.id, 'quantity': 2}
        response = self.client.post(url, data, format='json')
        updated_disbursements = RequestCart.objects.get(pk=request_to_add_to.id).cart_disbursements.all()
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        add_fail = False
        try:
            updated_disbursements.get(item=item_with_zero_tags)
        except ObjectDoesNotExist:
            add_fail = True
        self.assertEqual(add_fail, True)


class DeleteItemTestCases(APITestCase):
    fixtures = ['requests_action.json']

    def setUp(self):
        self.admin = User.objects.create_superuser(USERNAME, '', PASSWORD)
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
        request_to_delete_from = RequestCart.objects.create(owner=self.admin, status="active", reason="test cart",
                                                            staff_comment="this is an admin comment", staff=self.admin)
        Disbursement.objects.create(item=item_with_one_tag, quantity=1, cart=request_to_delete_from)
        second_disbursement = Disbursement.objects.create(item=item_with_zero_tags, quantity=2,
                                                          cart=request_to_delete_from)
        url = reverse('delete-from-cart', kwargs={'pk': str(second_disbursement.id)})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        delete_success = False
        # request no longer in request table
        try:
            Disbursement.objects.get(pk=second_disbursement.id)
        except ObjectDoesNotExist:
            delete_success = True
        self.assertEqual(delete_success, True)

    def test_delete_item_fail_not_active_shopping_cart(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        item_with_one_tag = Item.objects.create(name="oscilloscope", quantity=3, model_number="48979",
                                                description="oscilloscope")
        item_with_one_tag.tags.create(tag="test")
        item_with_zero_tags = Item.objects.create(name="resistor", quantity=5, model_number="456789",
                                                  description="resistor")
        request_to_delete_from = RequestCart.objects.create(owner=self.admin, status="outstanding", reason="test  cart",
                                                            staff_comment="this is an admin comment", staff=self.admin)
        Disbursement.objects.create(item=item_with_one_tag, quantity=1, cart=request_to_delete_from)
        second_disbursement = Disbursement.objects.create(item=item_with_zero_tags, quantity=2,
                                                          cart=request_to_delete_from)
        url = reverse('delete-from-cart', kwargs={'pk': str(second_disbursement.id)})
        response = self.client.delete(url)
        updated_disbursements = RequestCart.objects.get(pk=request_to_delete_from.id).cart_disbursements.all()
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        delete_fail = False
        if updated_disbursements.filter(pk=second_disbursement.id).exists():
            delete_fail = True
        self.assertEqual(delete_fail, True)

    def test_delete_item_fail_not_exists(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        item_with_one_tag = Item.objects.create(name="oscilloscope", quantity=3, model_number="48979",
                                                description="oscilloscope")
        item_with_one_tag.tags.create(tag="test")
        item_with_zero_tags = Item.objects.create(name="resistor", quantity=5, model_number="456789",
                                                  description="resistor")
        request_to_delete_from = RequestCart.objects.create(owner=self.admin, status="active", reason="test cart",
                                                            staff_comment="this is an admin comment", staff=self.admin)
        Disbursement.objects.create(item=item_with_one_tag, quantity=1, cart=request_to_delete_from)
        second_request = RequestCart.objects.create(owner=self.admin, status="outstanding", reason="test cart",
                                                     staff_comment="this is an admin comment", staff=self.admin)
        disbursement = Disbursement.objects.create(item=item_with_zero_tags, quantity=2, cart=second_request)
        # shoppping_cart_request_second_item doesn't exist in active shopping cart
        url = reverse('delete-from-cart', kwargs={'pk': str(disbursement.id)})
        response = self.client.delete(url)
        # should still be in another shopping
        disbursements = RequestCart.objects.get(pk=second_request.id).cart_disbursements.all()
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        # shopping cart request for second item should still be in another_shopping_cart
        delete_fail = False
        if disbursements.filter(pk=disbursement.id).exists():
            delete_fail = True
        self.assertEqual(delete_fail, True)


class PatchRequestTestCases(APITestCase):
    fixtures = ['requests_action.json', 'email_templates.json']

    def setUp(self):
        self.admin = User.objects.create_superuser(USERNAME, '', PASSWORD)
        self.receiver = User.objects.create_user(TEST_USERNAME, '', TEST_PASSWORD)
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
        item_with_zero_tags = Item.objects.create(name="resistor", quantity=5, model_number="456789")
        request_to_send = RequestCart.objects.create(owner=self.admin, status="active", reason="test cart",
                                                     staff_comment="this is an admin comment", staff=self.admin)
        Disbursement.objects.create(item=item_with_one_tag, quantity=1, cart=request_to_send)
        Disbursement.objects.create(item=item_with_zero_tags, quantity=2, cart=request_to_send)
        data = {'id': request_to_send.id, 'reason': "testing send cart"}
        url = reverse('send-cart', kwargs={'pk': str(request_to_send.id)})
        response = self.client.patch(url, data, format='json')
        updated_request = RequestCart.objects.get(pk=request_to_send.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(updated_request.status, "outstanding")
        equal_request_cart(self, json.loads(str(response.content, 'utf-8')), request_to_send.id)

    def test_send_cart_empty(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        item_with_one_tag = Item.objects.create(name="oscilloscope", quantity=3, model_number="48979",
                                                description="oscilloscope")
        item_with_one_tag.tags.create(tag="test")
        Item.objects.create(name="resistor", quantity=5, model_number="456789", description="resistor")
        request_to_send = RequestCart.objects.create(owner=self.admin, status="active", reason="test cart",
                                                            staff_comment="this is an admin comment", staff=self.admin)
        data = {'id': request_to_send.id, 'reason': "testing send empty cart should not work"}
        url = reverse('send-cart', kwargs={'pk': str(request_to_send.id)})
        response = self.client.patch(url, data, format='json')
        updated_request = RequestCart.objects.get(pk=request_to_send.id)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(updated_request.status, "active")

    def test_send_cart_fail_status(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        item_with_one_tag = Item.objects.create(name="oscilloscope", quantity=3, model_number="48979",
                                                description="oscilloscope")
        item_with_one_tag.tags.create(tag="test")
        item_with_zero_tags = Item.objects.create(name="resistor", quantity=5, model_number="456789", description="a")
        request_to_add = RequestCart.objects.create(owner=self.admin, status="outstanding", reason="test shopping cart",
                                                    staff_comment="this is an admin comment", staff=self.admin)
        Disbursement.objects.create(item=item_with_one_tag, quantity=1, cart=request_to_add)
        Disbursement.objects.create(item=item_with_zero_tags, quantity=2, cart=request_to_add)
        data = {'id': request_to_add.id, 'reason': "testing send cart"}
        url = reverse('send-cart', kwargs={'pk': str(request_to_add.id)})
        response = self.client.patch(url, data, format='json')
        updated_request = RequestCart.objects.get(pk=request_to_add.id)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(updated_request.status, request_to_add.status)
        self.assertEqual(updated_request.reason, request_to_add.reason)

    def test_modify_quantity(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        item_with_one_tag = Item.objects.create(name="oscilloscope", quantity=3, model_number="48979",
                                                description="oscilloscope")
        item_with_one_tag.tags.create(tag="test")
        request_to_modify = RequestCart.objects.create(owner=self.admin, status="active", reason="test cart",
                                                       staff_comment="this is an admin comment", staff=self.admin)
        disbursement = Disbursement.objects.create(item=item_with_one_tag, quantity=1, cart=request_to_modify)
        data = {'type': 'disbursement', 'quantity': 2}
        url = reverse('modify-quantity-requested', kwargs={'pk': str(disbursement.id)})
        response = self.client.patch(url, data, format='json')
        updated_disbursement = Disbursement.objects.get(pk=disbursement.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(updated_disbursement.quantity, data.get('quantity'))

    def test_modify_quantity_fail_status(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        item_with_one_tag = Item.objects.create(name="oscilloscope", quantity=3, model_number="48979",
                                                description="oscilloscope")
        item_with_one_tag.tags.create(tag="test")
        request_to_modify = RequestCart.objects.create(owner=self.admin, status="outstanding", reason="lol_cart",
                                                       staff_comment="this is an admin comment", staff=self.admin)
        disbursement = Disbursement.objects.create(item=item_with_one_tag, quantity=1, cart=request_to_modify)
        data = {'type': 'disbursement', 'quantity': 2}
        url = reverse('modify-quantity-requested', kwargs={'pk': str(disbursement.id)})
        response = self.client.patch(url, data, format='json')
        updated_disbursement = Disbursement.objects.get(pk=disbursement.id)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(updated_disbursement.quantity, disbursement.quantity)

    def test_modify_quantity_fail_negative_quantity(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        item_with_one_tag = Item.objects.create(name="oscilloscope", quantity=3, model_number="48979",
                                                description="oscilloscope")
        item_with_one_tag.tags.create(tag="test")
        request_to_modify = RequestCart.objects.create(owner=self.admin, status="active", reason="test shopping cart",
                                                       staff_comment="this is an admin comment", staff=self.admin)
        disbursement = Disbursement.objects.create(item=item_with_one_tag, quantity=1, cart=request_to_modify)
        data = {'type': 'disbursement', 'quantity': -5}
        url = reverse('modify-quantity-requested', kwargs={'pk': str(disbursement.id)})
        response = self.client.patch(url, data, format='json')
        updated_disbursement = Disbursement.objects.get(pk=disbursement.id)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(updated_disbursement.quantity, disbursement.quantity)

    def test_approve_shopping_cart(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        item_with_one_tag = Item.objects.create(name="oscilloscope", quantity=3, model_number="48979",
                                                description="oscilloscope")
        item_with_one_tag.tags.create(tag="test")
        request_to_approve = RequestCart.objects.create(owner=self.admin, status="outstanding", reason="test_cart")
        disbursement = Disbursement.objects.create(item=item_with_one_tag, quantity=2, cart=request_to_approve)
        data = {'id': request_to_approve.id, 'staff_comment': 'testing approve request'}
        url = reverse('approve-request-cart', kwargs={'pk': str(request_to_approve.id)})
        response = self.client.patch(url, data, format='json')
        updated_request = RequestCart.objects.get(pk=request_to_approve.id)
        updated_item = Item.objects.get(pk=item_with_one_tag.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(updated_request.status, "approved")
        self.assertEqual(updated_item.quantity, item_with_one_tag.quantity - disbursement.quantity)
        self.assertEqual(updated_request.staff_comment, "testing approve request")

    def test_approve_shopping_cart_fail_quantity(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        item_with_one_tag = Item.objects.create(name="oscilloscope", quantity=3, model_number="48979",
                                                description="oscilloscope")
        item_with_one_tag.tags.create(tag="test")
        request_to_approve = RequestCart.objects.create(owner=self.admin, status="outstanding", reason="test cart",
                                                        staff_comment="this is an admin comment", staff=self.admin)
        Disbursement.objects.create(item=item_with_one_tag, quantity=4, cart=request_to_approve)
        data = {'id': request_to_approve.id, 'staff_comment': 'testing approve request'}
        url = reverse('approve-request-cart', kwargs={'pk': str(request_to_approve.id)})
        response = self.client.patch(url, data, format='json')
        updated_item = Item.objects.get(pk=item_with_one_tag.id)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(item_with_one_tag.quantity, updated_item.quantity)

    def test_approve_shopping_cart_fail_status(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        item_with_one_tag = Item.objects.create(name="oscilloscope", quantity=3, model_number="48979",
                                                description="oscilloscope")
        item_with_one_tag.tags.create(tag="test")
        request_to_approve = RequestCart.objects.create(owner=self.admin, status="denied", reason="test cart",
                                                        staff_comment="this is an admin comment", staff=self.admin)
        Disbursement.objects.create(item=item_with_one_tag, quantity=4, cart=request_to_approve)
        data = {'id': request_to_approve.id, 'admin_comment': 'testing approve request'}
        url = reverse('approve-request-cart', kwargs={'pk': str(request_to_approve.id)})
        response = self.client.patch(url, data, format='json')
        updated_item = Item.objects.get(pk=item_with_one_tag.id)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(item_with_one_tag.quantity, updated_item.quantity)

    def test_deny_shopping_cart(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        item_with_one_tag = Item.objects.create(name="oscilloscope", quantity=3, model_number="48979",
                                                description="oscilloscope")
        item_with_one_tag.tags.create(tag="test")
        request_to_deny = RequestCart.objects.create(owner=self.admin, status="outstanding", reason="test cart")
        Disbursement.objects.create(item=item_with_one_tag, quantity=4, cart=request_to_deny)
        data = {'id': request_to_deny.id, 'staff_comment': 'testing deny request'}
        url = reverse('deny-request-cart', kwargs={'pk': str(request_to_deny.id)})
        response = self.client.patch(url, data, format='json')
        updated_request = RequestCart.objects.get(pk=request_to_deny.id)
        updated_item = Item.objects.get(pk=item_with_one_tag.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(updated_request.status, "denied")
        self.assertEqual(updated_item.quantity, item_with_one_tag.quantity)
        self.assertEqual(updated_request.staff_comment, "testing deny request")

    def test_deny_shopping_cart_fail(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        item_with_one_tag = Item.objects.create(name="oscilloscope", quantity=3, model_number="48979",
                                                description="oscilloscope")
        item_with_one_tag.tags.create(tag="test")
        request_to_deny = RequestCart.objects.create(owner=self.admin, status="cancelled", reason="test cart")
        Disbursement.objects.create(item=item_with_one_tag, quantity=2, cart=request_to_deny)
        data = {'id': request_to_deny.id, 'admin_comment': 'testing deny request'}
        url = reverse('deny-request-cart', kwargs={'pk': str(request_to_deny.id)})
        response = self.client.patch(url, data, format='json')
        updated_request = RequestCart.objects.get(pk=request_to_deny.id)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(request_to_deny.staff_comment, updated_request.staff_comment)
        self.assertEqual(request_to_deny.status, updated_request.status)

    def test_cancel_shopping_cart_fail(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        item_with_one_tag = Item.objects.create(name="oscilloscope", quantity=3, model_number="48979",
                                                description="oscilloscope")
        item_with_one_tag.tags.create(tag="test")
        request_to_cancel = RequestCart.objects.create(owner=self.admin, status="approved", reason="test shopping cart",
                                                       staff_comment="this is an admin comment", staff=self.admin)
        Disbursement.objects.create(item=item_with_one_tag, quantity=2, cart=request_to_cancel)
        data = {'id': request_to_cancel.id, 'comment': 'testing cancellation of request, should not work'}
        url = reverse('cancel-request-cart', kwargs={'pk': str(request_to_cancel.id)})
        response = self.client.patch(url, data, format='json')
        updated_request = RequestCart.objects.get(pk=request_to_cancel.id)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(request_to_cancel.reason, updated_request.reason)
        self.assertEqual(request_to_cancel.status, updated_request.status)

    def test_cancel_shopping_cart(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        item_with_one_tag = Item.objects.create(name="oscilloscope", quantity=3, model_number="48979",
                                                description="oscilloscope")
        item_with_one_tag.tags.create(tag="test")
        request_to_cancel = RequestCart.objects.create(owner=self.admin, status="outstanding", reason="test cart")
        Disbursement.objects.create(item=item_with_one_tag, quantity=2, cart=request_to_cancel)
        data = {'id': request_to_cancel.id, 'comment': 'testing cancellation of request, should not work'}
        url = reverse('cancel-request-cart', kwargs={'pk': str(request_to_cancel.id)})
        response = self.client.patch(url, data, format='json')
        updated_request= RequestCart.objects.get(pk=request_to_cancel.id)
        updated_item = Item.objects.get(pk=item_with_one_tag.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(item_with_one_tag.quantity, updated_item.quantity)
        self.assertEqual(updated_request.status, "cancelled")

    def test_fulfill_shopping_cart_failed(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        item_with_one_tag = Item.objects.create(name="test1", quantity=3, model_number="48979",
                                                description="test2")
        item_with_one_tag.tags.create(tag="try")
        request_to_fulfill = RequestCart.objects.create(owner=self.admin, status="outstanding", reason="test_cart",
                                                        staff_comment="this is comment", staff=self.admin)
        Disbursement.objects.create(item=item_with_one_tag, quantity=2, cart=request_to_fulfill)
        url = reverse('fulfill-request-cart', kwargs={'pk': str(request_to_fulfill.id)})
        response = self.client.patch(url, format='json')
        updated_request = RequestCart.objects.get(pk=request_to_fulfill.id)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(updated_request.status, request_to_fulfill.status)
        self.assertEqual(json.loads(str(response.content, 'utf-8'))['detail']
                         , "Request must be approved but is currently outstanding")

    def test_fulfill_shopping_cart(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        item_with_one_tag = Item.objects.create(name="oscillosasdcope", quantity=3, model_number="48979",
                                                description="oscsdilloscope")
        item_with_one_tag.tags.create(tag="taest")
        request_to_fulfill = RequestCart.objects.create(owner=self.admin, status="approved", reason="test_cart",
                                                       staff_comment="this is comment", staff=self.admin)
        Disbursement.objects.create(item=item_with_one_tag, quantity=2, cart=request_to_fulfill)
        url = reverse('fulfill-request-cart', kwargs={'pk': str(request_to_fulfill.id)})
        response = self.client.patch(url, format='json')
        updated_request = RequestCart.objects.get(pk=request_to_fulfill.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(updated_request.status, 'fulfilled')

    def test_admin_disburse(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        item = Item.objects.create(name="test_item", quantity=3)
        request_cart = RequestCart.objects.create(owner=self.admin, status="active", reason="test_cart",
                                                  staff_comment="this is comment", staff=self.admin)
        disbursement = Disbursement.objects.create(cart=request_cart, item=item, quantity=1)
        url = reverse('dispense-request-cart', kwargs={'pk': str(request_cart.id)})
        data = {'owner_id': self.receiver.id, 'staff_comment': 'lit'}
        response = self.client.patch(path=url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_item = Item.objects.get(pk=item.id)
        self.assertEqual(updated_item.quantity, item.quantity - disbursement.quantity)
        updated_request = RequestCart.objects.get(pk=request_cart.id)
        self.assertEqual(updated_request.status, 'fulfilled')
        self.assertEqual(updated_request.owner, self.receiver)
        self.assertEqual(updated_request.staff, self.admin)
        self.assertEqual(updated_request.staff_comment, data.get('staff_comment'))

    def test_admin_disburse_inactive_cart(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        item = Item.objects.create(name="test_item_2", quantity=3)
        request_cart = RequestCart.objects.create(owner=self.admin, status="approved", reason="test_cart",
                                                  staff_comment="this is comment", staff=self.admin)
        Disbursement.objects.create(cart=request_cart, item=item, quantity=1)
        url = reverse('dispense-request-cart', kwargs={'pk': str(request_cart.id)})
        data = {'owner_id': self.receiver.id, 'staff_comment': 'lit'}
        response = self.client.patch(path=url, data=data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(json.loads(str(response.content, 'utf-8'))['detail']
                         , "Cart needs to be active")

    def test_admin_disburse_insufficient_item(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        item = Item.objects.create(name="test_item_3", quantity=3)
        request_cart = RequestCart.objects.create(owner=self.admin, status="active", reason="test_cart",
                                                  staff_comment="this is comment", staff=self.admin)
        Disbursement.objects.create(cart=request_cart, item=item, quantity=100)
        url = reverse('dispense-request-cart', kwargs={'pk': str(request_cart.id)})
        data = {'owner_id': self.receiver.id, 'staff_comment': 'lit'}
        response = self.client.patch(path=url, data=data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(json.loads(str(response.content, 'utf-8'))['detail']
                         , "Cannot dispense due to insufficient items")
