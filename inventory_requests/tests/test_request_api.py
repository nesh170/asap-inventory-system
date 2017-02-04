import json
from datetime import timedelta, timezone, datetime

from django.contrib.auth.models import User
from django.urls import reverse
from oauth2_provider.admin import Application
from oauth2_provider.models import AccessToken
from oauth2_provider.settings import oauth2_settings
from rest_framework import status
from rest_framework.test import APITestCase

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
#this function tests if the JSON representation of a request (either returned from a get request
def equal_request(test_client, request_json, request_id):
    request = Request.objects.get(pk=request_id)
    test_client.assertEqual(request_json.get('owner'), request.owner.id)
    test_client.assertEqual(request_json.get('status'), request.status)
    test_client.assertEqual(request_json.get('item').get('id'), request.item.id)
    test_client.assertEqual(request_json.get('item').get('name'), request.item.name)
    test_client.assertEqual(request_json.get('item').get('quantity'), request.item.quantity)
    test_client.assertEqual(request_json.get('quantity'), request.quantity)
    test_client.assertEqual(request_json.get('reason'), request.reason)
    test_client.assertEqual(request_json.get('admin_timestamp'), request.admin_timestamp)
    print(request.admin)
    print(request_json.get('admin'))
    test_client.assertEqual(request_json.get('admin'), request.admin.id)


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
        print(json.loads(str(response.content, 'utf-8')))
        json_request_list = json.loads(str(response.content, 'utf-8'))
        #verifies the number of requests returned by the GET request is the same as the number of requests in the database
        #self.assertEqual(json.loads(str(response.content, 'utf-8'))['count'], Request.objects.count())
        # for each request returned by GET request, all equal_request on each one to verify the JSON representation
        # contains the same information as the information in the database
        [equal_request(self, json_request, json_request.get('id')) for json_request in json_request_list]





