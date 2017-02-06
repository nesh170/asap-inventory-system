import json
from datetime import timedelta, timezone, datetime

from django.contrib.auth.models import User
from django.urls import reverse
from oauth2_provider.admin import Application
from oauth2_provider.models import AccessToken
from oauth2_provider.settings import oauth2_settings
from rest_framework import status
from rest_framework.test import APITestCase

from inventory_logger.action_enum import ActionEnum
from inventory_logger.models import Action
from inventory_requests.models import Request
from items.models import Item
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

def setup_logging():
    Action.objects.create(color="1", tag=ActionEnum.REQUEST_APPROVED.value)
    Action.objects.create(color="2", tag=ActionEnum.REQUEST_CANCELLED.value)
    Action.objects.create(color="3", tag=ActionEnum.REQUEST_DENIED.value)
    Action.objects.create(color="4", tag=ActionEnum.REQUEST_CREATED.value)
    Action.objects.create(color="5", tag=ActionEnum.DISBURSED.value)



#this function tests if the JSON representation of a request (either returned from a get request
def equal_request(test_client, request_json, request_id):
    request = Request.objects.get(pk=request_id)
    test_client.assertEqual(request_json.get('owner'), request.owner.id) if type(request_json.get('owner')) is int \
        else test_client.assertEqual(request_json.get('owner').get('id'), request.owner.id)
    test_client.assertEqual(request_json.get('status'), request.status)
    test_client.assertEqual(request_json.get('item').get('id'), request.item.id)
    test_client.assertEqual(request_json.get('item').get('name'), request.item.name)
    test_client.assertEqual(request_json.get('item').get('quantity'), request.item.quantity)
    test_client.assertEqual(request_json.get('quantity'), request.quantity)
    test_client.assertEqual(request_json.get('reason'), request.reason)
    test_client.assertEqual(request_json.get('admin_comment'), request.admin_comment)
    if request_json.get('admin') is not None:
        test_client.assertEqual(request_json.get('admin'), request.admin.id) if type(request_json.get('admin')) is int \
            else test_client.assertEqual(request_json.get('admin').get('id'), request.admin.id)

def equal_after_disburse(test_client, disburse_json, item_id, original_item_quantity):
    item = Item.objects.get(pk=item_id)
    test_client.assertEqual(disburse_json.get('item_id'), item.id)
    test_client.assertEqual(original_item_quantity - disburse_json.get('quantity'), item.quantity)
class GetRequestTestCases(APITestCase):
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
        setup_logging()
        item_with_one_tag = Item.objects.create(name="quad 2-input NAND gate", quantity=0, model_number="48979",
                                                description="Jameco", location="hudson 116")
        item_with_one_tag.tags.create(tag="test")

        request_to_create = Request.objects.create(owner=self.admin, status="outstanding", item=item_with_one_tag, quantity=2, reason="test request",
                                                   admin_comment="this is an admin comment", admin=self.admin)

        #basic_request = Request.objects.create(owner=self.admin, status="outstanding", item=item_with_one_tag, quantity=2, reason="basic request")

    def test_get_requests(self):
        url = reverse('requests-list')
        self.client.force_authenticate(user=self.admin, token=self.tok)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # converts response to a string and then to a JSON dictionary, and then gets results attribute of it
        json_request_list = json.loads(str(response.content, 'utf-8'))['results']
        #verifies the number of requests returned by the GET request is the same as the number of requests in the database
        #self.assertEqual(json.loads(str(response.content, 'utf-8'))['count'], Request.objects.count())
        # for each request returned by GET request, all equal_request on each one to verify the JSON representation
        # contains the same information as the information in the database
        [equal_request(self, json_request, json_request.get('id')) for json_request in json_request_list]
    def test_get_detailed_request(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        for request_id in Request.objects.values_list('id', flat=True):
            url = reverse('detailed-request', kwargs={'pk': str(request_id)})
            #make the get request
            response = self.client.get(url)
            #compare the JSON response received from the GET request to what is in database
            equal_request(self, json.loads(str(response.content, 'utf-8')), request_id)
    def test_get_requests_user(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        url = reverse('requests-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json_request_list = json.loads(str(response.content, 'utf-8'))['results']
        [equal_request(self, json_request, json_request.get('id')) for json_request in json_request_list]
class PostRequestTestCases(APITestCase):
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
        setup_logging()

    def test_create_request(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        item_with_one_tag = Item.objects.create(name="oscilloscope", quantity=3, model_number="48979",
                                                description="oscilloscope", location="hudson 116")
        item_with_one_tag.tags.create(tag="test")
        item_id = item_with_one_tag.id
        url = reverse('requests-list')
        data = {'item_id': item_id, 'reason': 'testing create post request', 'quantity': 2}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data['owner'] = self.admin.id
        data['status'] = 'outstanding'
        data['item'] = {'id': item_id, 'name': item_with_one_tag.name, 'quantity':item_with_one_tag.quantity}

        json_request = json.loads(str(response.content, 'utf-8'))
        # test if data that was in POST request is the same as what was just stored in the database based on request_id
        #data is request_json, and id comes from the response, which is then used to load request from database
        equal_request(self, data, json_request.get('id'))

class PatchRequestTestCases(APITestCase):
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
        setup_logging()

    def test_approve_request(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        item_with_one_tag = Item.objects.create(name="oscilloscope", quantity=3, model_number="48979",
                                                description="oscilloscope", location="hudson 116")
        item_with_one_tag.tags.create(tag="test")
        request_to_approve = Request.objects.create(owner=self.admin, status="outstanding", item=item_with_one_tag,
                                                   quantity=2, reason="test request")
        data = {'id': request_to_approve.id, 'admin_comment': 'testing approve request'}
        url = reverse('approve-request', kwargs={'pk': str(request_to_approve.id)})
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json_request = json.loads(str(response.content, 'utf-8'))
        data['owner'] = self.admin.id
        data['status'] = 'approved'
        data['item'] = {'id': item_with_one_tag.id, 'name': item_with_one_tag.name, 'quantity':item_with_one_tag.quantity - request_to_approve.quantity}
        data['quantity'] = request_to_approve.quantity
        data['reason'] = request_to_approve.reason
        data['admin_comment'] = "approval reason is : " + data.get('admin_comment')
        equal_request(self, data, json_request.get('id'))

    def test_deny_request(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        item_with_one_tag = Item.objects.create(name="oscilloscope", quantity=3, model_number="48979",
                                                description="oscilloscope", location="hudson 116")
        item_with_one_tag.tags.create(tag="test")
        request_to_deny = Request.objects.create(owner=self.admin, status="outstanding", item=item_with_one_tag,
                                                   quantity=2, reason="test request", admin_comment="this is an admin comment",
                                                 admin=self.admin)
        data = {'id': request_to_deny.id, 'admin_comment': 'testing deny request'}
        url = reverse('deny-request', kwargs={'pk': str(request_to_deny.id)})
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json_request = json.loads(str(response.content, 'utf-8'))
        data['owner'] = self.admin.id
        data['status'] = 'denied'
        data['item'] = {'id': item_with_one_tag.id, 'name': item_with_one_tag.name,
                        'quantity': item_with_one_tag.quantity}
        data['quantity'] = request_to_deny.quantity
        data['reason'] = request_to_deny.reason
        data['admin_comment'] = request_to_deny.admin_comment + ' denial reason is : ' + data.get('admin_comment')
        equal_request(self, data, json_request.get('id'))

    def test_cancel_request(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        item_with_one_tag = Item.objects.create(name="oscilloscope", quantity=3, model_number="48979",
                                                description="oscilloscope", location="hudson 116")
        item_with_one_tag.tags.create(tag="test")
        request_to_cancel = Request.objects.create(owner=self.admin, status="outstanding", item=item_with_one_tag,
                                                 quantity=2, reason="test request",
                                                 admin_comment="this is an admin comment",
                                                 admin=self.admin)
        data = {'id': request_to_cancel.id, 'reason': 'testing cancellation of request'}
        url = reverse('cancel-request', kwargs={'pk': str(request_to_cancel.id)})
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json_request = json.loads(str(response.content, 'utf-8'))
        data['owner'] = self.admin.id
        data['status'] = 'cancelled'
        data['item'] = {'id': item_with_one_tag.id, 'name': item_with_one_tag.name,
                        'quantity': item_with_one_tag.quantity}
        data['quantity'] = request_to_cancel.quantity
        data['reason'] = request_to_cancel.reason + ' cancellation reason is : ' + data.get('reason')
        data['admin_comment'] = "this is an admin comment"
        equal_request(self, data, json_request.get('id'))
class DisburseRequestTestCase(APITestCase):
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
        setup_logging()


    def test_disburse(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        item_with_one_tag = Item.objects.create(name="oscilloscope", quantity=3, model_number="48979",
                                      description="oscilloscope", location="hudson 116")
        item_with_one_tag.tags.create(tag="test")
        url = reverse('disburse')
        data = {'item_id': item_with_one_tag.id, 'quantity': 2, 'receiver': 'ankit', 'disburse_comment': 'testing disburse'}
        response = self.client.post(url, data, format='json')
        json_disburse_response = json.loads(str(response.content, 'utf-8'))
        equal_after_disburse(self, data, json_disburse_response.get('item_id'), item_with_one_tag.quantity)